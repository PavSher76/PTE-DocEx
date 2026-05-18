"""REST API datacentric-ядра контекста проекта и экспорт документов по привязанной схеме."""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import ProjectProfile
from app.project_context import (
    InvestmentProjectPackage,
    build_investment_project_ai_context,
    build_minstroy_design_assignment_xml,
    default_investment_project_package,
)
from app.project_context.schemas_api import (
    ProjectProfileCreate,
    ProjectProfileRead,
    ProjectProfileSummary,
    ProjectProfileUpdate,
)
from app.schemas import InvestmentProjectExportResponse

router = APIRouter(prefix="/project-context", tags=["project-context"])


def _to_read(row: ProjectProfile) -> ProjectProfileRead:
    return ProjectProfileRead(
        id=row.id,
        project_cipher=row.project_cipher,
        name=row.name,
        description=row.description,
        primary_schema_binding=row.primary_schema_binding,
        package=InvestmentProjectPackage.model_validate(row.context_payload),
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


def _export_for_binding(binding: str, package: InvestmentProjectPackage) -> InvestmentProjectExportResponse:
    if binding != "design_assignment_01_00":
        raise HTTPException(
            status_code=422,
            detail=f"Генератор для привязки схемы «{binding}» не подключён.",
        )
    try:
        xml = build_minstroy_design_assignment_xml(package.assignment)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return InvestmentProjectExportResponse(
        ai_context_json=build_investment_project_ai_context(package),
        design_assignment_xml=xml,
    )


@router.get("/package-template", response_model=InvestmentProjectPackage)
def get_package_template() -> InvestmentProjectPackage:
    """Эталонный JSON-пакет для редактирования в UI и проверки контракта."""

    return default_investment_project_package()


@router.post("/export", response_model=InvestmentProjectExportResponse)
def export_package(body: InvestmentProjectPackage) -> InvestmentProjectExportResponse:
    """Экспорт без сохранения (ядро генерации по каноническому пакету)."""

    return _export_for_binding("design_assignment_01_00", body)


@router.get("/profiles", response_model=list[ProjectProfileSummary])
def list_profiles(db: Session = Depends(get_db)) -> list[ProjectProfileSummary]:
    rows = db.query(ProjectProfile).order_by(ProjectProfile.updated_at.desc()).all()
    return [
        ProjectProfileSummary(
            id=r.id,
            project_cipher=r.project_cipher,
            name=r.name,
            primary_schema_binding=r.primary_schema_binding,
            updated_at=r.updated_at,
        )
        for r in rows
    ]


@router.post("/profiles", response_model=ProjectProfileRead, status_code=201)
def create_profile(body: ProjectProfileCreate, db: Session = Depends(get_db)) -> ProjectProfileRead:
    now = datetime.utcnow()
    row = ProjectProfile(
        project_cipher=body.project_cipher,
        name=body.name,
        description=body.description,
        primary_schema_binding=body.primary_schema_binding,
        context_payload=body.package.model_dump(mode="json"),
        created_at=now,
        updated_at=now,
    )
    db.add(row)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Профиль с таким шифром проекта уже существует.") from exc
    db.refresh(row)
    return _to_read(row)


@router.get("/profiles/{profile_id}", response_model=ProjectProfileRead)
def get_profile(profile_id: int, db: Session = Depends(get_db)) -> ProjectProfileRead:
    row = db.get(ProjectProfile, profile_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Профиль не найден.")
    return _to_read(row)


@router.patch("/profiles/{profile_id}", response_model=ProjectProfileRead)
def update_profile(
    profile_id: int,
    body: ProjectProfileUpdate,
    db: Session = Depends(get_db),
) -> ProjectProfileRead:
    row = db.get(ProjectProfile, profile_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Профиль не найден.")
    if body.name is not None:
        row.name = body.name
    if body.description is not None:
        row.description = body.description
    if body.primary_schema_binding is not None:
        row.primary_schema_binding = body.primary_schema_binding
    if body.package is not None:
        row.context_payload = body.package.model_dump(mode="json")
    row.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(row)
    return _to_read(row)


@router.delete("/profiles/{profile_id}", status_code=204)
def delete_profile(profile_id: int, db: Session = Depends(get_db)) -> None:
    row = db.get(ProjectProfile, profile_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Профиль не найден.")
    db.delete(row)
    db.commit()


@router.post("/profiles/{profile_id}/export", response_model=InvestmentProjectExportResponse)
def export_profile(profile_id: int, db: Session = Depends(get_db)) -> InvestmentProjectExportResponse:
    row = db.get(ProjectProfile, profile_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Профиль не найден.")
    package = InvestmentProjectPackage.model_validate(row.context_payload)
    return _export_for_binding(row.primary_schema_binding, package)
