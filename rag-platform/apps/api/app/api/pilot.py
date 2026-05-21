from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from rag_pilot.runner import PilotRunner
from rag_schemas.pilot import (
    PilotBootstrapResponse,
    PilotFeedbackCreate,
    PilotFeedbackRead,
    PilotRunRequest,
    PilotRunResponse,
)
from rag_storage.config import get_settings
from rag_storage.db import get_db_session
from rag_storage.models import PilotFeedback
from rag_storage.repositories.project import ProjectRepository

router = APIRouter(prefix="/pilot", tags=["pilot"])


def get_db():
    yield from get_db_session()


@router.post("/bootstrap", response_model=PilotBootstrapResponse)
def bootstrap_pilot(
    project_id: str | None = None,
    db: Session = Depends(get_db),
) -> PilotBootstrapResponse:
    runner = PilotRunner(db)
    pid, created = runner.bootstrap(project_id)
    return PilotBootstrapResponse(
        project_id=pid,
        name="Пилот ИТЦ — комплект ПД/РД",
        created=created,
        message="Проект создан." if created else "Проект уже существует.",
    )


@router.post("/{project_id}/run", response_model=PilotRunResponse)
def run_pilot(
    project_id: str,
    body: PilotRunRequest,
    db: Session = Depends(get_db),
) -> PilotRunResponse:
    if ProjectRepository(db).get_by_project_id(project_id) is None:
        raise HTTPException(status_code=404, detail="Проект не найден. POST /pilot/bootstrap")
    try:
        return PilotRunner(db).run(
            project_id,
            check_ids=body.check_ids,
            run_query=body.run_query,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/feedback", response_model=PilotFeedbackRead, status_code=201)
def create_feedback(
    body: PilotFeedbackCreate,
    db: Session = Depends(get_db),
) -> PilotFeedbackRead:
    if ProjectRepository(db).get_by_project_id(body.project_id) is None:
        raise HTTPException(status_code=404, detail="Проект не найден.")
    row = PilotFeedback(
        project_id=body.project_id,
        source_type=body.source_type,
        source_id=body.source_id,
        rating=body.rating,
        comment=body.comment,
        lesson_tags=body.lesson_tags,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return PilotFeedbackRead.model_validate(row)


@router.get("/{project_id}/feedback", response_model=list[PilotFeedbackRead])
def list_feedback(
    project_id: str,
    db: Session = Depends(get_db),
) -> list[PilotFeedbackRead]:
    rows = list(
        db.scalars(
            select(PilotFeedback)
            .where(PilotFeedback.project_id == project_id)
            .order_by(PilotFeedback.created_at.desc())
            .limit(50)
        )
    )
    return [PilotFeedbackRead.model_validate(r) for r in rows]
