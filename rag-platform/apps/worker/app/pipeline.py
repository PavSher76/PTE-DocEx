"""Конвейер обработки: parse → tokenize → embed → index (Sprint 2: hybrid vectors)."""

from __future__ import annotations

import json
import logging
import tempfile
from pathlib import Path
from uuid import UUID

from rag_embeddings.dense import DenseEmbedder
from rag_embeddings.sparse import SparseEmbedder
from rag_parsers.factory import parse_document
from rag_storage.collections import text_collection_for
from rag_storage.config import Settings, get_settings
from rag_storage.minio_client import MinioStorage
from rag_storage.models import (
    Document,
    DocumentVersion,
    EngineeringToken,
    ProcessingJob,
    Requirement,
    SourceFile,
)
from rag_storage.qdrant_client import QdrantStore
from rag_pipeline.logging_utils import pipeline_step
from rag_tokenizers.engineering import EngineeringTokenizer
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.drawing_index import delete_drawing_pages_for_version, index_drawings_for_pdf

LOG = logging.getLogger("rag.pipeline")


def process_job(session: Session, job_id: UUID, settings: Settings | None = None) -> None:
    settings = settings or get_settings()
    job = session.scalar(
        select(ProcessingJob)
        .where(ProcessingJob.id == job_id)
        .options(
            joinedload(ProcessingJob.version)
            .joinedload(DocumentVersion.document)
            .joinedload(Document.project)
        )
    )
    if job is None:
        raise ValueError(f"Job {job_id} не найден")

    source = session.scalar(select(SourceFile).where(SourceFile.version_id == job.version_id))
    if source is None:
        raise ValueError("Source file не найден")

    document = job.version.document
    project = document.project
    text_collection = text_collection_for(document, settings)

    LOG.info(
        "═══ Старт конвейера job=%s | project=%s | file=%s | collection=%s | rag=%s ═══",
        job_id,
        project.project_id,
        source.filename,
        text_collection,
        document.rag_collection or "default",
    )

    def set_status(status: str, stage: str | None = None, error: str | None = None) -> None:
        job.status = status
        job.stage = stage
        job.error_message = error
        session.flush()
        if error:
            LOG.error("job=%s status=%s stage=%s | %s", job_id, status, stage, error)
        else:
            LOG.info("job=%s status=%s stage=%s", job_id, status, stage or "—")

    tmp_path: Path | None = None
    orm_tokens: list[EngineeringToken] = []

    try:
        with pipeline_step(
            job_id,
            "download+parse",
            project_id=project.project_id,
            filename=source.filename,
            collection=text_collection,
        ):
            set_status("parsing", "parse")
            storage = MinioStorage(settings)
            raw = storage.download_bytes(source.storage_uri)
            suffix = Path(source.filename).suffix or ".bin"
            with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
                tmp.write(raw)
                tmp_path = Path(tmp.name)
            LOG.info("job=%s скачан %s байт", job_id, len(raw))

            elements, parser_name = parse_document(
                tmp_path,
                source.file_type,
                settings,
                rag_collection=document.rag_collection,
            )
            LOG.info("job=%s парсер=%s элементов=%s", job_id, parser_name, len(elements))

            parser_uri = storage.upload_bytes(
                json.dumps(
                    [
                        {
                            "text": e.text,
                            "type": e.element_type,
                            "page": e.page_number,
                            "meta": e.metadata,
                        }
                        for e in elements
                    ],
                    ensure_ascii=False,
                ).encode("utf-8"),
                project_id=project.project_id,
                filename=f"{source.id}-parser.json",
                content_type="application/json",
            )
            source.parser_output_uri = parser_uri

        with pipeline_step(job_id, "tokenize", project_id=project.project_id, filename=source.filename):
            set_status("tokenizing", "tokenize")
            tokenizer = EngineeringTokenizer()
            token_dicts = tokenizer.tokenize_elements(
                elements,
                project_id=project.project_id,
                document_id=document.id,
                version_id=job.version_id,
                source_uri=source.storage_uri,
                stage=document.stage,
                discipline=document.discipline,
                document_code=document.document_code,
            )
            LOG.info("job=%s токенов=%s", job_id, len(token_dicts))

            session.query(Requirement).filter(Requirement.document_id == document.id).delete()
            session.query(EngineeringToken).filter(EngineeringToken.version_id == job.version_id).delete()
            delete_drawing_pages_for_version(session, job.version_id)

            requirements: list[Requirement] = []
            for item in token_dicts:
                orm_tokens.append(
                    EngineeringToken(
                        id=item["id"],
                        project_id=item["project_id"],
                        document_id=item["document_id"],
                        version_id=item["version_id"],
                        parent_token_id=item.get("parent_token_id"),
                        page_number=item.get("page_number"),
                        element_type=item["element_type"],
                        text=item["text"],
                        bbox=item.get("bbox"),
                        source_uri=item["source_uri"],
                        stage=item.get("stage"),
                        discipline=item.get("discipline"),
                        document_code=item.get("document_code"),
                        revision=item.get("revision"),
                        status=item.get("status"),
                        ntd_refs=item.get("ntd_refs", []),
                        requirement_refs=item.get("requirement_refs", []),
                        quality=item.get("quality", "complete"),
                        extra={**(item.get("extra") or {}), "parser": parser_name},
                    )
                )
                if item["element_type"] == "requirement":
                    requirements.append(
                        Requirement(
                            project_id=item["project_id"],
                            document_id=item["document_id"],
                            source_token_id=item["id"],
                            text=item["text"],
                            status="draft",
                            ntd_refs=item.get("ntd_refs", []),
                        )
                    )
            session.add_all(orm_tokens + requirements)
            session.flush()
            LOG.info("job=%s требований в БД=%s", job_id, len(requirements))

        with pipeline_step(
            job_id,
            "embed+index",
            project_id=project.project_id,
            collection=text_collection,
            extra={"tokens": len(orm_tokens)},
        ):
            set_status("embedding", "embed")
            dense = DenseEmbedder(settings)
            sparse = SparseEmbedder()
            qdrant = QdrantStore(settings)
            qdrant.ensure_collections(dense.dimension)
            qdrant.delete_by_document_version(text_collection, job.version_id)

            drawing_tokens_count = 0
            if source.file_type == "pdf" and settings.drawing_index_enabled and tmp_path:
                set_status("parsing", "drawings")
                try:
                    drawing_tokens_count = index_drawings_for_pdf(
                        session,
                        pdf_path=tmp_path,
                        document=document,
                        version=job.version,
                        project_id=project.project_id,
                        source_uri=source.storage_uri,
                        settings=settings,
                    )
                    LOG.info("job=%s чертежных токенов=%s", job_id, drawing_tokens_count)
                except RuntimeError as exc:
                    LOG.warning("job=%s индекс чертежей пропущен: %s", job_id, exc)

            for i, row in enumerate(orm_tokens, start=1):
                dense_vector = dense.embed(row.text)
                sparse_indices, sparse_values = sparse.embed(row.text)
                qdrant.upsert_token(
                    text_collection,
                    token_id=row.id,
                    dense_vector=dense_vector,
                    sparse_indices=sparse_indices,
                    sparse_values=sparse_values,
                    payload={
                        "project_id": row.project_id,
                        "document_id": str(row.document_id),
                        "version_id": str(row.version_id),
                        "document_name": document.name,
                        "document_code": row.document_code,
                        "page_number": row.page_number,
                        "element_type": row.element_type,
                        "text": row.text[:4000],
                        "bbox": row.bbox,
                        "source_uri": row.source_uri,
                        "revision": row.revision,
                        "status": row.status,
                        "ntd_refs": row.ntd_refs or [],
                        "section_path": (row.extra or {}).get("section_path", []),
                        "metadata": row.extra or {},
                    },
                )
                if i % 50 == 0 or i == len(orm_tokens):
                    LOG.info(
                        "job=%s проиндексировано %s/%s → %s",
                        job_id,
                        i,
                        len(orm_tokens),
                        text_collection,
                    )

            if drawing_tokens_count:
                job.stage = f"index+drawings:{drawing_tokens_count}"
                session.flush()

            set_status("indexed", "index")

        session.commit()
        LOG.info(
            "═══ Готово job=%s | project=%s | tokens=%s | collection=%s ═══",
            job_id,
            project.project_id,
            len(orm_tokens),
            text_collection,
        )
    except Exception as exc:
        session.rollback()
        job = session.get(ProcessingJob, job_id)
        if job:
            job.status = "failed"
            job.error_message = str(exc)
            session.commit()
        LOG.exception("═══ Ошибка конвейера job=%s ═══", job_id)
        raise
