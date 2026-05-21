"""API модуля «Документы ИСМ»."""

from __future__ import annotations

import zipfile

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, Response, UploadFile
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.ism.batch_service import create_batch_upload, enqueue_batch_processing, extract_zip_entries
from app.ism.interface_graph import get_graph
from app.ism.models import IsmDocument, IsmProcess, IsmProcessingJob, IsmUploadBatch
from app.ism.reports import build_batch_report, render_batch_report_pdf
from app.ism.processor import process_document_job
from app.ism.repository import get_document_detail, get_queue, list_documents, list_errors
from app.ism.schemas import (
    IsmBatchUploadResponse,
    IsmDocumentDetailRead,
    IsmDocumentRead,
    IsmErrorRead,
    IsmBatchReportRead,
    IsmGraphRead,
    IsmProcessCreate,
    IsmProcessRead,
    IsmProcessUpdate,
    IsmQueueDashboardRead,
    IsmReviewQueueRead,
    IsmReviewUpdate,
)
from app.ism.seed import seed_ism_processes
from app.services.ism_extract import is_ism_allowed_filename

router = APIRouter(prefix="/ism", tags=["ism-documents"])


@router.get("/processes", response_model=list[IsmProcessRead])
def list_processes(db: Session = Depends(get_db)) -> list[IsmProcess]:
    seed_ism_processes(db)
    return list(db.query(IsmProcess).order_by(IsmProcess.process_code).all())


@router.post("/processes", response_model=IsmProcessRead)
def create_process(body: IsmProcessCreate, db: Session = Depends(get_db)) -> IsmProcess:
    if db.query(IsmProcess).filter(IsmProcess.process_code == body.process_code).first():
        raise HTTPException(status_code=409, detail="Процесс с таким кодом уже существует.")
    row = IsmProcess(**body.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@router.patch("/processes/{process_id}", response_model=IsmProcessRead)
def update_process(
    process_id: str, body: IsmProcessUpdate, db: Session = Depends(get_db)
) -> IsmProcess:
    row = db.get(IsmProcess, process_id)
    if not row:
        raise HTTPException(status_code=404, detail="Процесс не найден.")
    for key, value in body.model_dump(exclude_unset=True).items():
        setattr(row, key, value)
    db.commit()
    db.refresh(row)
    return row


@router.get("/documents/queue/dashboard", response_model=IsmQueueDashboardRead)
def queue_dashboard(batch_id: str | None = None, db: Session = Depends(get_db)) -> IsmQueueDashboardRead:
    items = get_queue(db, batch_id=batch_id)
    by_status: dict[str, int] = {}
    for item in items:
        by_status[item.status] = by_status.get(item.status, 0) + 1
    return IsmQueueDashboardRead(batch_id=batch_id, total=len(items), by_status=by_status, items=items)


@router.get("/documents/graph", response_model=IsmGraphRead)
def interface_graph(
    batch_id: str | None = None,
    process_id: str | None = None,
    document_type: str | None = None,
    owner: str | None = None,
    status: str | None = None,
    db: Session = Depends(get_db),
) -> IsmGraphRead:
    return get_graph(
        db,
        batch_id=batch_id,
        process_id=process_id,
        document_type=document_type,
        owner=owner,
        status=status,
    )


@router.get("/documents/errors/list", response_model=list[IsmErrorRead])
def errors_list(batch_id: str | None = None, db: Session = Depends(get_db)) -> list[IsmErrorRead]:
    return list_errors(db, batch_id=batch_id)


@router.get("/documents", response_model=list[IsmDocumentRead])
def list_docs(
    batch_id: str | None = None,
    process_id: str | None = None,
    db: Session = Depends(get_db),
) -> list[IsmDocumentRead]:
    return list_documents(db, batch_id=batch_id, process_id=process_id)


@router.get("/documents/{document_id}", response_model=IsmDocumentDetailRead)
def get_doc(document_id: str, db: Session = Depends(get_db)) -> IsmDocumentDetailRead:
    detail = get_document_detail(db, document_id)
    if not detail:
        raise HTTPException(status_code=404, detail="Документ не найден.")
    return detail


@router.post("/documents/batch-upload", response_model=IsmBatchUploadResponse)
async def batch_upload(
    background_tasks: BackgroundTasks,
    files: list[UploadFile] = File(...),
    ism_process_id: str | None = Form(None),
    document_type: str = Form("OTHER"),
    owner: str = Form("ИСМ"),
    status: str = Form("active"),
    revision: str = Form("A"),
    discipline: str | None = Form(None),
    comment: str = Form(""),
    title: str = Form(""),
    project_cipher: str | None = Form(None),
    db: Session = Depends(get_db),
) -> IsmBatchUploadResponse:
    settings = get_settings()
    if not files:
        raise HTTPException(status_code=400, detail="Выберите файлы.")

    payload: list[tuple[str, bytes]] = []
    for upload in files:
        name = upload.filename or "file"
        if not is_ism_allowed_filename(name):
            raise HTTPException(status_code=400, detail=f"Неподдерживаемый формат: {name}")
        data = await upload.read()
        if len(data) > settings.max_upload_mb * 1024 * 1024:
            raise HTTPException(status_code=413, detail=f"Файл {name} слишком большой.")
        payload.append((name, data))

    batch, jobs = create_batch_upload(
        db,
        settings,
        files=payload,
        ism_process_id=ism_process_id,
        document_type=document_type,
        owner=owner,
        status=status,
        revision=revision,
        discipline=discipline,
        comment=comment,
        title=title,
        project_cipher=project_cipher,
    )
    enqueue_batch_processing(batch.id, jobs, background_tasks)
    return IsmBatchUploadResponse(
        batch_id=batch.id,
        documents_total=len(jobs),
        jobs_queued=len(jobs),
        message=f"Пакет принят: {len(jobs)} документов в очереди обработки.",
    )


@router.post("/documents/upload-zip", response_model=IsmBatchUploadResponse)
async def upload_zip(
    background_tasks: BackgroundTasks,
    archive: UploadFile = File(...),
    ism_process_id: str | None = Form(None),
    document_type: str = Form("OTHER"),
    owner: str = Form("ИСМ"),
    status: str = Form("active"),
    revision: str = Form("A"),
    discipline: str | None = Form(None),
    comment: str = Form(""),
    title: str = Form(""),
    project_cipher: str | None = Form(None),
    db: Session = Depends(get_db),
) -> IsmBatchUploadResponse:
    settings = get_settings()
    data = await archive.read()
    if len(data) > settings.max_upload_mb * 1024 * 1024 * 5:
        raise HTTPException(status_code=413, detail="ZIP слишком большой.")
    try:
        entries = extract_zip_entries(data)
    except zipfile.BadZipFile as exc:
        raise HTTPException(status_code=400, detail="Некорректный ZIP.") from exc
    if not entries:
        raise HTTPException(status_code=400, detail="В архиве нет поддерживаемых файлов.")

    batch, jobs = create_batch_upload(
        db,
        settings,
        files=entries,
        ism_process_id=ism_process_id,
        document_type=document_type,
        owner=owner,
        status=status,
        revision=revision,
        discipline=discipline,
        comment=comment,
        title=title or archive.filename or "ZIP пакет",
        project_cipher=project_cipher,
    )
    enqueue_batch_processing(batch.id, jobs, background_tasks)
    return IsmBatchUploadResponse(
        batch_id=batch.id,
        documents_total=len(jobs),
        jobs_queued=len(jobs),
        message=f"Из ZIP извлечено {len(jobs)} документов.",
    )


@router.get("/batches/{batch_id}/review-queue", response_model=IsmReviewQueueRead)
def review_queue(batch_id: str, db: Session = Depends(get_db)) -> IsmReviewQueueRead:
    batch = db.get(IsmUploadBatch, batch_id)
    if not batch:
        raise HTTPException(status_code=404, detail="Пакет не найден.")
    items = list_documents(db, batch_id=batch_id)
    pending = [d for d in items if d.review_status == "pending"]
    return IsmReviewQueueRead(batch_id=batch_id, items=pending or items)


@router.patch("/documents/{document_id}/review", response_model=IsmDocumentRead)
def update_document_review(
    document_id: str,
    body: IsmReviewUpdate,
    db: Session = Depends(get_db),
) -> IsmDocumentRead:
    doc = db.get(IsmDocument, document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Документ не найден.")
    doc.review_status = body.review_status
    doc.review_notes = body.review_notes
    doc.reviewed_at = __import__("datetime").datetime.utcnow()
    db.commit()
    rows = list_documents(db, batch_id=doc.batch_id)
    row = next((r for r in rows if r.document_id == document_id), None)
    if not row:
        raise HTTPException(status_code=404, detail="Документ не найден.")
    return row


@router.get("/batches/{batch_id}/report.json", response_model=IsmBatchReportRead)
def batch_report_json(batch_id: str, db: Session = Depends(get_db)) -> IsmBatchReportRead:
    batch = db.get(IsmUploadBatch, batch_id)
    if not batch:
        raise HTTPException(status_code=404, detail="Пакет не найден.")
    report = batch.report_json or build_batch_report(db, batch_id)
    return IsmBatchReportRead(batch_id=batch_id, report=report)


@router.get("/batches/{batch_id}/report.pdf")
def batch_report_pdf(batch_id: str, db: Session = Depends(get_db)) -> Response:
    batch = db.get(IsmUploadBatch, batch_id)
    if not batch:
        raise HTTPException(status_code=404, detail="Пакет не найден.")
    report = batch.report_json or build_batch_report(db, batch_id)
    pdf_bytes = render_batch_report_pdf(report)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="ism-batch-{batch_id[:8]}.pdf"'},
    )


@router.post("/batches/{batch_id}/finalize")
def finalize_batch(batch_id: str, db: Session = Depends(get_db)) -> dict:
    from app.ism.batch_finalize import maybe_finalize_batch

    batch = db.get(IsmUploadBatch, batch_id)
    if not batch:
        raise HTTPException(status_code=404, detail="Пакет не найден.")
    maybe_finalize_batch(db, get_settings(), batch_id)
    db.refresh(batch)
    return {"batch_id": batch_id, "status": batch.status, "ai_pipeline_status": batch.ai_pipeline_status}


@router.post("/jobs/{job_id}/retry")
def retry_job(job_id: str, background_tasks: BackgroundTasks, db: Session = Depends(get_db)) -> dict:
    job = db.get(IsmProcessingJob, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Задача не найдена.")
    job.status = "queued"
    job.progress = 0
    job.error_message = None
    job.finished_at = None
    db.commit()
    background_tasks.add_task(process_document_job, job.document_id, job.id)
    return {"status": "queued", "job_id": job_id}


@router.post("/jobs/{job_id}/cancel")
def cancel_job(job_id: str, db: Session = Depends(get_db)) -> dict:
    job = db.get(IsmProcessingJob, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Задача не найдена.")
    job.status = "cancelled"
    job.finished_at = job.finished_at or __import__("datetime").datetime.utcnow()
    db.commit()
    return {"status": "cancelled", "job_id": job_id}


# Совместимость с ранним MVP (пакеты на файловой системе)
@router.get("/packages")
def list_legacy_packages() -> list:
    from app.services.ism_registry import list_ism_packages

    return list_ism_packages(get_settings())
