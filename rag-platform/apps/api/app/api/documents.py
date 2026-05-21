from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from redis import Redis
from rq import Queue
from sqlalchemy.orm import Session

from rag_schemas.document import (
    DocumentStatusResponse,
    DocumentTokensResponse,
    DocumentUploadResponse,
    ProcessingJobRead,
)
from rag_schemas.engineering_token import EngineeringTokenPayload
from rag_schemas.enums import ElementType, JobStatus
from rag_storage.config import get_settings
from rag_storage.db import get_db_session
from rag_storage.minio_client import MinioStorage
from rag_storage.models import EngineeringToken as EngineeringTokenORM
from rag_storage.repositories.document import DocumentRepository
from rag_storage.repositories.project import ProjectRepository
from rag_storage.repositories.token import TokenRepository
from rag_storage.document_delete import delete_document_completely

router = APIRouter()


def get_db():
    yield from get_db_session()


def _detect_file_type(filename: str, content_type: str) -> str:
    lower = filename.lower()
    if lower.endswith(".pdf"):
        return "pdf"
    if lower.endswith(".docx"):
        return "docx"
    if lower.endswith(".xlsx") or lower.endswith(".xls"):
        return "xlsx"
    if lower.endswith((".png", ".jpg", ".jpeg", ".tiff")):
        return "image"
    if "pdf" in content_type:
        return "pdf"
    return "unknown"


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    project_id: str = Form(...),
    file: UploadFile = File(...),
    document_code: str | None = Form(None),
    stage: str | None = Form(None),
    discipline: str | None = Form(None),
    rag_collection: str | None = Form(
        None,
        description="project_analysis — коллекция «Анализ проекта»",
    ),
    db: Session = Depends(get_db),
) -> DocumentUploadResponse:
    settings = get_settings()
    project = ProjectRepository(db).get_by_project_id(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Проект не найден. Создайте POST /projects.")

    data = await file.read()
    max_bytes = settings.max_upload_mb * 1024 * 1024
    if len(data) > max_bytes:
        raise HTTPException(status_code=413, detail=f"Файл больше {settings.max_upload_mb} МБ")

    filename = file.filename or "upload.bin"
    content_type = file.content_type or "application/octet-stream"
    file_type = _detect_file_type(filename, content_type)

    storage = MinioStorage(settings)
    storage_uri = storage.upload_bytes(
        data,
        project_id=project_id,
        filename=filename,
        content_type=content_type,
    )

    doc_repo = DocumentRepository(db)
    document, version, _source, job = doc_repo.create_document_with_upload(
        project=project,
        name=filename,
        filename=filename,
        content_type=content_type,
        file_type=file_type,
        size_bytes=len(data),
        storage_uri=storage_uri,
        document_code=document_code,
        stage=stage,
        discipline=discipline,
        rag_collection=(rag_collection or "").strip() or None,
    )

    redis = Redis.from_url(settings.redis_url)
    queue = Queue("ingest", connection=redis)
    rq_job = queue.enqueue(
        "app.tasks.process_document_version",
        str(job.id),
        job_timeout=3600,
    )
    doc_repo.update_job_status(job, job.status, rq_job_id=rq_job.id)

    return DocumentUploadResponse(
        document_id=document.id,
        version_id=version.id,
        source_file_id=_source.id,
        job_id=job.id,
        status=JobStatus(job.status),
    )


@router.delete("/{document_id}", status_code=204)
def delete_document(document_id: UUID, db: Session = Depends(get_db)) -> None:
    """Полное удаление: векторы Qdrant, файлы MinIO, записи PostgreSQL."""
    if not delete_document_completely(db, document_id, get_settings()):
        raise HTTPException(status_code=404, detail="Документ не найден.")


@router.post("/{document_id}/process")
def reprocess_document(document_id: UUID, db: Session = Depends(get_db)) -> DocumentUploadResponse:
    document = DocumentRepository(db).get_document(document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Документ не найден.")
    job = DocumentRepository(db).get_latest_job_for_document(document_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Задача обработки не найдена.")
    settings = get_settings()
    redis = Redis.from_url(settings.redis_url)
    queue = Queue("ingest", connection=redis)
    rq_job = queue.enqueue("app.tasks.process_document_version", str(job.id), job_timeout=3600)
    DocumentRepository(db).update_job_status(job, "uploaded", rq_job_id=rq_job.id)
    return DocumentUploadResponse(
        document_id=document.id,
        version_id=job.version_id,
        source_file_id=job.version_id,
        job_id=job.id,
        status=JobStatus(job.status),
        message="Повторная обработка поставлена в очередь",
    )


@router.get("/{document_id}/status", response_model=DocumentStatusResponse)
def document_status(document_id: UUID, db: Session = Depends(get_db)) -> DocumentStatusResponse:
    doc_repo = DocumentRepository(db)
    document = doc_repo.get_document(document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Документ не найден.")
    job = doc_repo.get_latest_job_for_document(document_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Задача не найдена.")
    tokens_count = doc_repo.count_tokens_for_version(job.version_id)
    return DocumentStatusResponse(
        document_id=document_id,
        version_id=job.version_id,
        job=ProcessingJobRead.model_validate(job),
        tokens_count=tokens_count,
    )


@router.get("/{document_id}/tokens", response_model=DocumentTokensResponse)
def document_tokens(
    document_id: UUID,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db),
) -> DocumentTokensResponse:
    doc_repo = DocumentRepository(db)
    document = doc_repo.get_document(document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Документ не найден.")
    job = doc_repo.get_latest_job_for_document(document_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Задача не найдена.")

    rows = TokenRepository(db).list_by_version(job.version_id, limit=limit, offset=offset)
    items = [
        EngineeringTokenPayload(
            token_id=row.id,
            project_id=row.project_id,
            document_id=row.document_id,
            version_id=row.version_id,
            stage=row.stage,  # type: ignore[arg-type]
            discipline=row.discipline,
            document_code=row.document_code,
            sheet_number=row.sheet_number,
            page_number=row.page_number,
            element_type=ElementType(row.element_type),
            text=row.text,
            bbox=row.bbox,
            source_uri=row.source_uri,
            revision=row.revision,
            status=row.status,
            ntd_refs=row.ntd_refs or [],
            requirement_refs=row.requirement_refs or [],
            parent_token_id=row.parent_token_id,
            quality=row.quality,  # type: ignore[arg-type]
            metadata=row.extra or {},
            created_at=row.created_at,
        )
        for row in rows
    ]
    return DocumentTokensResponse(
        document_id=document_id,
        version_id=job.version_id,
        total=doc_repo.count_tokens_for_version(job.version_id),
        items=items,
    )
