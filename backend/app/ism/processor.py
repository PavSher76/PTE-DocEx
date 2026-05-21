"""Конвейер обработки одного документа ИСМ."""

from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path

from sqlalchemy.orm import Session

from app.config import Settings, get_settings
from app.database import SessionLocal
from app.ism.batch_finalize import maybe_finalize_batch
from app.ism.interface_graph import build_interfaces_for_batch
from app.ism.models import (
    IsmDocument,
    IsmDocumentElement,
    IsmDocumentFile,
    IsmDocumentVersion,
    IsmProcessingError,
    IsmProcessingJob,
    IsmRagToken,
    IsmRequirement,
)
from app.ism.parse_pipeline import guess_document_type, parse_file
from app.ism.qdrant_sync import index_document_vectors
from app.ism.tokenizer import tokenize_document
from app.services.ism_rag import ingest_ism_package_to_rag

logger = logging.getLogger(__name__)


def _set_job(db: Session, job: IsmProcessingJob, status: str, *, progress: int, stage: str | None = None) -> None:
    job.status = status
    job.progress = progress
    job.stage = stage
    if status in {"parsing", "extracting", "tokenizing", "embedding", "queued"} and job.started_at is None:
        job.started_at = datetime.utcnow()
    if status in {"indexed", "failed", "needs_review", "cancelled"}:
        job.finished_at = datetime.utcnow()
    db.commit()


def process_document_job(document_id: str, job_id: str) -> None:
    settings = get_settings()
    db = SessionLocal()
    job: IsmProcessingJob | None = None
    doc: IsmDocument | None = None
    try:
        job = db.get(IsmProcessingJob, job_id)
        doc = db.get(IsmDocument, document_id)
        if not job or not doc:
            return
        if job.status == "cancelled":
            return

        file_row = db.query(IsmDocumentFile).filter(IsmDocumentFile.document_id == document_id).first()
        if not file_row:
            _fail(db, job, doc, "parse", "Файл не найден в хранилище.")
            return

        path = Path(file_row.storage_path)
        _set_job(db, job, "parsing", progress=10, stage="detect_type")
        try:
            parsed = parse_file(path, settings, filename=file_row.filename)
        except Exception as exc:
            _fail(db, job, doc, "parse", str(exc))
            return

        _set_job(db, job, "extracting", progress=35, stage="structure")
        if not doc.title:
            doc.title = file_row.filename
        if not doc.code and parsed.metadata.get("detected_code"):
            doc.code = str(parsed.metadata["detected_code"])
        if doc.document_type == "OTHER":
            doc.document_type = guess_document_type(file_row.filename, parsed.full_text)
        doc.parse_raw_json = {
            "metadata": parsed.metadata,
            "references": parsed.references[:50],
            "full_text_preview": parsed.full_text[:8000],
        }
        doc.ai_summary = parsed.full_text[:1200]
        doc.updated_at = datetime.utcnow()

        version = db.query(IsmDocumentVersion).filter(IsmDocumentVersion.document_id == document_id).first()
        if not version:
            version = IsmDocumentVersion(document_id=document_id, revision=doc.revision)
            db.add(version)
            db.flush()

        db.query(IsmDocumentElement).filter(IsmDocumentElement.document_id == document_id).delete()
        db.query(IsmRequirement).filter(IsmRequirement.document_id == document_id).delete()

        for el in parsed.elements:
            bbox = el.bbox
            if isinstance(bbox, list):
                bbox = {"rect": bbox}
            db.add(
                IsmDocumentElement(
                    document_id=document_id,
                    version_id=version.id,
                    element_type=el.element_type,
                    section=el.section,
                    text=el.text,
                    source_page=el.source_page,
                    source_table=el.source_table,
                    bbox=bbox,
                    extra=el.extra,
                )
            )
        requirements: list[IsmRequirement] = []
        for req_text in parsed.requirements[:100]:
            req = IsmRequirement(document_id=document_id, text=req_text[:2000], section="")
            db.add(req)
            requirements.append(req)

        db.commit()
        elements = list(
            db.query(IsmDocumentElement).filter(IsmDocumentElement.document_id == document_id).all()
        )
        requirements = list(
            db.query(IsmRequirement).filter(IsmRequirement.document_id == document_id).all()
        )

        _set_job(db, job, "tokenizing", progress=55, stage="tokens")
        tokens = tokenize_document(doc, elements)
        db.query(IsmRagToken).filter(IsmRagToken.document_id == document_id).delete()
        for t in tokens:
            db.add(t)
        db.commit()

        rag_error: str | None = None
        if settings.rag_enabled:
            _set_job(db, job, "embedding", progress=75, stage="qdrant_index")
            try:
                index_document_vectors(settings, db, doc, tokens=tokens, requirements=requirements)
            except Exception as exc:
                logger.warning("ISM Qdrant index failed: %s", exc)
                rag_error = str(exc)

            _set_job(db, job, "embedding", progress=85, stage="rag_upload")
            summary = ingest_ism_package_to_rag(
                settings,
                file_paths=[path],
                package_id=doc.batch_id or document_id,
                project_cipher=None,
            )
            if summary.files and summary.files[0].document_id:
                job.rag_document_id = summary.files[0].document_id
            if summary.files and summary.files[0].error:
                rag_error = rag_error or summary.files[0].error

        if rag_error:
            _set_job(db, job, "needs_review", progress=95, stage="rag_partial")
            job.error_message = rag_error
        else:
            _set_job(db, job, "indexed", progress=100, stage="done")

        if doc.batch_id:
            batch_docs = list(db.query(IsmDocument).filter(IsmDocument.batch_id == doc.batch_id).all())
            build_interfaces_for_batch(db, doc.batch_id, batch_docs)
            maybe_finalize_batch(db, settings, doc.batch_id)

    except Exception as exc:
        logger.exception("ISM job failed doc=%s: %s", document_id, exc)
        if job and doc:
            _fail(db, job, doc, "pipeline", str(exc))
    finally:
        db.close()


def _fail(db: Session, job: IsmProcessingJob, doc: IsmDocument, error_type: str, message: str) -> None:
    job.status = "failed"
    job.error_message = message
    job.finished_at = datetime.utcnow()
    db.add(
        IsmProcessingError(
            job_id=job.id,
            document_id=doc.id,
            error_type=error_type,
            message=message,
        )
    )
    db.commit()
    if doc.batch_id:
        maybe_finalize_batch(db, get_settings(), doc.batch_id)
