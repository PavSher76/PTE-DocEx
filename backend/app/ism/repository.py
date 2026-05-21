"""Запросы к БД модуля ИСМ."""

from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.ism.models import (
    IsmDocument,
    IsmDocumentFile,
    IsmProcessingError,
    IsmProcessingJob,
    IsmProcess,
    IsmRequirement,
    IsmInterface,
    IsmDocumentElement,
    IsmRagToken,
)
from app.ism.schemas import IsmDocumentRead, IsmDocumentDetailRead, IsmQueueItemRead, IsmErrorRead


def list_documents(
    db: Session,
    *,
    batch_id: str | None = None,
    process_id: str | None = None,
    limit: int = 200,
) -> list[IsmDocumentRead]:
    q = select(IsmDocument).order_by(IsmDocument.created_at.desc()).limit(limit)
    if batch_id:
        q = q.where(IsmDocument.batch_id == batch_id)
    if process_id:
        q = q.where(IsmDocument.ism_process_id == process_id)
    rows = db.scalars(q).all()
    result: list[IsmDocumentRead] = []
    for doc in rows:
        file_row = db.scalar(
            select(IsmDocumentFile).where(IsmDocumentFile.document_id == doc.id).limit(1)
        )
        job = db.scalar(
            select(IsmProcessingJob)
            .where(IsmProcessingJob.document_id == doc.id)
            .order_by(IsmProcessingJob.created_at.desc())
            .limit(1)
        )
        iface_count = db.scalar(
            select(func.count())
            .select_from(IsmInterface)
            .where(
                (IsmInterface.source_document_id == doc.id)
                | (IsmInterface.target_document_id == doc.id)
            )
        )
        tokens_count = db.scalar(
            select(func.count()).select_from(IsmRagToken).where(IsmRagToken.document_id == doc.id)
        )
        result.append(
            IsmDocumentRead(
                document_id=doc.id,
                ism_process_id=doc.ism_process_id,
                document_type=doc.document_type,
                title=doc.title,
                code=doc.code,
                revision=doc.revision,
                status=doc.status,
                owner=doc.owner,
                discipline=doc.discipline,
                related_processes=doc.related_processes or [],
                related_documents=doc.related_documents or [],
                batch_id=doc.batch_id,
                filename=file_row.filename if file_row else None,
                file_type=file_row.file_type if file_row else None,
                job_status=job.status if job else None,
                job_progress=job.progress if job else 0,
                tokens_count=int(tokens_count or 0),
                interfaces_count=int(iface_count or 0),
                review_status=doc.review_status or "pending",
                created_at=doc.created_at,
            )
        )
    return result


def get_document_detail(db: Session, document_id: str) -> IsmDocumentDetailRead | None:
    doc = db.get(IsmDocument, document_id)
    if not doc:
        return None
    rows = list_documents(db)
    row = next((r for r in rows if r.document_id == document_id), None)
    if not row:
        file_row = db.scalar(
            select(IsmDocumentFile).where(IsmDocumentFile.document_id == document_id).limit(1)
        )
        job = db.scalar(
            select(IsmProcessingJob).where(IsmProcessingJob.document_id == document_id).limit(1)
        )
        row = IsmDocumentRead(
            document_id=doc.id,
            ism_process_id=doc.ism_process_id,
            document_type=doc.document_type,
            title=doc.title,
            code=doc.code,
            revision=doc.revision,
            status=doc.status,
            owner=doc.owner,
            discipline=doc.discipline,
            batch_id=doc.batch_id,
            filename=file_row.filename if file_row else None,
            file_type=file_row.file_type if file_row else None,
            job_status=job.status if job else None,
            job_progress=job.progress if job else 0,
            created_at=doc.created_at,
        )
    return IsmDocumentDetailRead(
        **row.model_dump(),
        requirements=[{"id": r.id, "text": r.text, "section": r.section} for r in doc.requirements],
        interfaces=[
            {
                "id": i.id,
                "link_type": i.link_type,
                "target_document_id": i.target_document_id,
                "reference_text": i.reference_text,
                "confidence": i.confidence,
            }
            for i in db.scalars(
                select(IsmInterface).where(
                    (IsmInterface.source_document_id == document_id)
                    | (IsmInterface.target_document_id == document_id)
                )
            ).all()
        ],
        elements=[
            {
                "id": e.id,
                "element_type": e.element_type,
                "section": e.section,
                "text": e.text[:500],
            }
            for e in db.scalars(
                select(IsmDocumentElement).where(IsmDocumentElement.document_id == document_id).limit(80)
            ).all()
        ],
        rag_tokens_sample=[
            {"token_type": t.token_type, "section": t.section, "text": t.text[:300]}
            for t in db.scalars(
                select(IsmRagToken).where(IsmRagToken.document_id == document_id).limit(20)
            ).all()
        ],
        ai_summary=doc.ai_summary,
        parse_raw_json=doc.parse_raw_json,
    )


def get_queue(db: Session, *, batch_id: str | None = None) -> list[IsmQueueItemRead]:
    q = select(IsmProcessingJob).order_by(IsmProcessingJob.created_at.desc())
    if batch_id:
        q = q.where(IsmProcessingJob.batch_id == batch_id)
    jobs = db.scalars(q.limit(500)).all()
    items: list[IsmQueueItemRead] = []
    for job in jobs:
        doc = db.get(IsmDocument, job.document_id)
        file_row = db.scalar(
            select(IsmDocumentFile).where(IsmDocumentFile.document_id == job.document_id).limit(1)
        )
        items.append(
            IsmQueueItemRead(
                job_id=job.id,
                document_id=job.document_id,
                batch_id=job.batch_id,
                filename=file_row.filename if file_row else "—",
                document_code=doc.code if doc else "",
                status=job.status,
                stage=job.stage,
                progress=job.progress,
                error_message=job.error_message,
                created_at=job.created_at,
            )
        )
    return items


def list_errors(db: Session, *, batch_id: str | None = None, limit: int = 100) -> list[IsmErrorRead]:
    q = select(IsmProcessingError).order_by(IsmProcessingError.created_at.desc()).limit(limit)
    if batch_id:
        q = q.join(IsmProcessingJob, IsmProcessingJob.id == IsmProcessingError.job_id).where(
            IsmProcessingJob.batch_id == batch_id
        )
    errors = db.scalars(q).all()
    out: list[IsmErrorRead] = []
    for err in errors:
        file_row = db.scalar(
            select(IsmDocumentFile).where(IsmDocumentFile.document_id == err.document_id).limit(1)
        )
        out.append(
            IsmErrorRead(
                id=err.id,
                document_id=err.document_id,
                job_id=err.job_id,
                filename=file_row.filename if file_row else "—",
                error_type=err.error_type,
                message=err.message,
                created_at=err.created_at,
            )
        )
    return out
