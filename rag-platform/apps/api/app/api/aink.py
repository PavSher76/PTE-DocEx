from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import PlainTextResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from rag_aink.runner import CheckRunner
from rag_retrievers.hybrid import HybridRetriever
from rag_schemas.aink import (
    RequirementTraceResponse,
    RunChecksRequest,
    RunChecksResponse,
    CheckRunSummary,
)
from rag_schemas.query import SearchFilters
from rag_storage.config import get_settings
from rag_storage.db import get_db_session
from rag_storage.models import CheckRun, Requirement
from rag_storage.repositories.project import ProjectRepository

router = APIRouter(prefix="/projects", tags=["aink"])


def get_db():
    yield from get_db_session()


@router.get("/{project_id}/checks")
def list_available_checks(project_id: str, db: Session = Depends(get_db)) -> dict:
    _ensure_project(db, project_id)
    return {"project_id": project_id, "checks": CheckRunner(db).available_checks()}


@router.post("/{project_id}/checks/run", response_model=RunChecksResponse)
def run_checks(
    project_id: str,
    body: RunChecksRequest,
    db: Session = Depends(get_db),
) -> RunChecksResponse:
    _ensure_project(db, project_id)
    runner = CheckRunner(db)
    report, markdown = runner.run(project_id, check_ids=body.check_ids)

    row = CheckRun(
        id=report.run_id,
        project_id=project_id,
        overall_status=report.overall_status.value,
        report_json=report.model_dump(mode="json"),
        report_markdown=markdown,
    )
    db.add(row)
    db.commit()

    return RunChecksResponse(
        run_id=report.run_id,
        report=report,
        markdown_url_hint=f"/projects/{project_id}/checks/{report.run_id}/report.md",
    )


@router.get("/{project_id}/checks/runs", response_model=list[CheckRunSummary])
def list_check_runs(project_id: str, db: Session = Depends(get_db)) -> list[CheckRunSummary]:
    _ensure_project(db, project_id)
    rows = list(
        db.scalars(
            select(CheckRun)
            .where(CheckRun.project_id == project_id)
            .order_by(CheckRun.created_at.desc())
            .limit(20)
        )
    )
    return [
        CheckRunSummary(
            run_id=row.id,
            project_id=row.project_id,
            overall_status=row.overall_status,
            created_at=row.created_at.isoformat(),
            checks_count=len(row.report_json.get("checks", [])),
        )
        for row in rows
    ]


@router.get("/{project_id}/checks/latest", response_model=RunChecksResponse)
def latest_check_run(project_id: str, db: Session = Depends(get_db)) -> RunChecksResponse:
    _ensure_project(db, project_id)
    row = db.scalar(
        select(CheckRun)
        .where(CheckRun.project_id == project_id)
        .order_by(CheckRun.created_at.desc())
    )
    if row is None:
        raise HTTPException(status_code=404, detail="Прогоны AI-NK не найдены.")
    from rag_aink.schemas import CheckReport

    report = CheckReport.model_validate(row.report_json)
    return RunChecksResponse(
        run_id=row.id,
        report=report,
        markdown_url_hint=f"/projects/{project_id}/checks/{row.id}/report.md",
    )


@router.get("/{project_id}/checks/{run_id}/report.md", response_class=PlainTextResponse)
def get_report_markdown(
    project_id: str,
    run_id: UUID,
    db: Session = Depends(get_db),
) -> PlainTextResponse:
    row = db.get(CheckRun, run_id)
    if row is None or row.project_id != project_id:
        raise HTTPException(status_code=404, detail="Отчёт не найден.")
    return PlainTextResponse(row.report_markdown, media_type="text/markdown; charset=utf-8")


def _ensure_project(db: Session, project_id: str) -> None:
    if ProjectRepository(db).get_by_project_id(project_id) is None:
        raise HTTPException(status_code=404, detail="Проект не найден.")


# --- Requirements trace (этап 11, базовая реализация в Sprint 4) ---

requirements_router = APIRouter(tags=["requirements"])


@requirements_router.get("/projects/{project_id}/requirements")
def list_requirements(project_id: str, db: Session = Depends(get_db)) -> list[dict]:
    _ensure_project(db, project_id)
    rows = list(db.scalars(select(Requirement).where(Requirement.project_id == project_id)))
    return [
        {
            "id": str(row.id),
            "text": row.text,
            "status": row.status,
            "ntd_refs": row.ntd_refs or [],
            "document_id": str(row.document_id) if row.document_id else None,
        }
        for row in rows
    ]


@requirements_router.post("/requirements/{requirement_id}/trace", response_model=RequirementTraceResponse)
def trace_requirement(requirement_id: UUID, db: Session = Depends(get_db)) -> RequirementTraceResponse:
    req = db.get(Requirement, requirement_id)
    if req is None:
        raise HTTPException(status_code=404, detail="Требование не найдено.")

    settings = get_settings()
    retriever = HybridRetriever(settings)
    hits = retriever.search(
        project_id=req.project_id,
        query=req.text,
        filters=SearchFilters(),
        top_k=8,
        use_hybrid=True,
    )
    drawings_hits = retriever.search(
        project_id=req.project_id,
        query=req.text,
        filters=SearchFilters(),
        top_k=5,
        collection=settings.qdrant_collection_drawings_text,
    )
    related = [
        {
            "token_id": str(h.token_id),
            "score": h.score,
            "element_type": h.element_type,
            "page": h.page_number,
            "text": h.text[:300],
            "source": "documents",
        }
        for h in hits
    ] + [
        {
            "token_id": str(h.token_id),
            "score": h.score,
            "element_type": h.element_type,
            "page": h.page_number,
            "text": h.text[:300],
            "source": "drawings",
        }
        for h in drawings_hits
    ]
    status = "traced" if related else "no_evidence"
    return RequirementTraceResponse(
        requirement_id=requirement_id,
        requirement_text=req.text,
        related_hits=sorted(related, key=lambda x: x["score"], reverse=True),
        status=status,
    )
