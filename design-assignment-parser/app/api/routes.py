from __future__ import annotations

import json
from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, File, HTTPException, UploadFile
from fastapi.responses import FileResponse, PlainTextResponse

from app.api.schemas import JobCreatedResponse, JobStatusResponse, ValidationReportResponse
from app.config import get_settings
from app.models.pipeline_state import JobStatus
from app.pipeline.job_store import get_job, save_job
from app.pipeline.orchestrator import run_pipeline

router = APIRouter()


def _run_async(job_id: UUID, pdf_path: Path, corrections: Path | None) -> None:
    job = get_job(job_id)
    if job is None:
        return
    run_pipeline(pdf_path, corrections_path=corrections, job=job)


@router.post("/parse-design-assignment", response_model=JobCreatedResponse)
async def parse_design_assignment(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
) -> JobCreatedResponse:
    if not (file.filename or "").lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Ожидается PDF.")

    settings = get_settings()
    settings.jobs_dir.mkdir(parents=True, exist_ok=True)

    from app.models.pipeline_state import PipelineJob

    job = PipelineJob()
    work = settings.jobs_dir / str(job.job_id)
    work.mkdir(parents=True, exist_ok=True)
    pdf_path = work / (file.filename or "upload.pdf")
    pdf_path.write_bytes(await file.read())
    job.source_pdf = pdf_path
    job.work_dir = work
    job.status = JobStatus.queued
    save_job(job)

    background_tasks.add_task(_run_async, job.job_id, pdf_path, None)
    return JobCreatedResponse(job_id=job.job_id, status=job.status.value)


@router.get("/jobs/{job_id}", response_model=JobStatusResponse)
def get_job_status(job_id: UUID) -> JobStatusResponse:
    job = get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job не найден.")
    return JobStatusResponse(
        job_id=job.job_id,
        status=job.status.value,
        pdf_type=job.pdf_type,
        stages_completed=job.stages_completed,
        quality_gates=[g.model_dump() for g in job.quality_gates],
        errors=job.errors,
        artifacts=list(job.artifacts.keys()),
        created_at=job.created_at,
        updated_at=job.updated_at,
    )


@router.get("/jobs/{job_id}/canonical-json")
def get_canonical_json(job_id: UUID):
    job = get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job не найден.")
    path = job.artifacts.get("canonical.json")
    if not path or not path.exists():
        raise HTTPException(status_code=404, detail="canonical.json ещё не готов.")
    return json.loads(path.read_text(encoding="utf-8"))


@router.get("/jobs/{job_id}/xml")
def get_xml(job_id: UUID):
    job = get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job не найден.")
    path = job.artifacts.get("design_assignment.xml")
    if not path or not path.exists():
        raise HTTPException(status_code=404, detail="XML ещё не готов.")
    return PlainTextResponse(path.read_text(encoding="utf-8"), media_type="application/xml")


@router.get("/jobs/{job_id}/validation-report", response_model=ValidationReportResponse)
def get_validation_report(job_id: UUID) -> ValidationReportResponse:
    job = get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job не найден.")
    val = job.stage_metrics.get("validation")
    if not val:
        raise HTTPException(status_code=404, detail="Отчёт валидации ещё не готов.")
    return ValidationReportResponse(
        valid=bool(val.get("valid")),
        errors=val.get("errors", []),
        missing_required_fields=val.get("missing_required_fields", []),
    )


@router.get("/jobs/{job_id}/tokens")
def get_tokens(job_id: UUID):
    job = get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job не найден.")
    path = job.artifacts.get("rag_tokens.json")
    if not path or not path.exists():
        raise HTTPException(status_code=404, detail="Токены ещё не готовы.")
    return json.loads(path.read_text(encoding="utf-8"))


@router.get("/jobs/{job_id}/artifacts/{name}")
def download_artifact(job_id: UUID, name: str):
    job = get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job не найден.")
    path = job.artifacts.get(name)
    if not path or not path.exists():
        raise HTTPException(status_code=404, detail="Артефакт не найден.")
    return FileResponse(path)
