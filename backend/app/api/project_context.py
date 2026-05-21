"""REST API datacentric-ядра контекста проекта и экспорт документов по привязанной схеме."""

import logging
from datetime import datetime

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.models import ProjectProfile
from app.project_context import (
    InvestmentProjectPackage,
    build_investment_project_ai_context,
    build_minstroy_design_assignment_xml,
    default_investment_project_package,
)
from app.project_context.chat_prompt import (
    DEFAULT_PROJECT_CONTEXT_CHAT_PROMPT,
    build_project_context_chat_prompt,
)
from app.project_context.document_text import extract_document_text
from app.project_context.schemas_api import (
    ProjectContextChatRequest,
    ProjectContextChatResponse,
    ProjectContextDocumentIngestResponse,
    ProjectProfileCreate,
    ProjectProfileRead,
    ProjectProfileSummary,
    ProjectProfileUpdate,
)
from app.schemas import InvestmentProjectExportResponse, OllamaModelsResponse
from app.services.ollama import OllamaClient
from app.services.storage import save_upload

router = APIRouter(prefix="/project-context", tags=["project-context"])
logger = logging.getLogger(__name__)


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


@router.get("/models", response_model=OllamaModelsResponse)
async def list_ollama_models() -> OllamaModelsResponse:
    settings = get_settings()
    try:
        result = await OllamaClient(settings).list_models()
    except Exception as exc:
        logger.exception("list_ollama_models failed")
        return OllamaModelsResponse(
            models=[],
            default_model=settings.ollama_model,
            ollama_reachable=False,
            error=f"Ошибка при получении списка моделей: {exc}",
        )
    return OllamaModelsResponse(
        models=result.models,
        default_model=settings.ollama_model,
        ollama_reachable=result.error is None,
        error=result.error,
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


def _get_profile_row(profile_id: int, db: Session) -> ProjectProfile:
    row = db.get(ProjectProfile, profile_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Профиль не найден.")
    return row


@router.post("/profiles/{profile_id}/ingest-document", response_model=ProjectContextDocumentIngestResponse)
async def ingest_profile_document(
    profile_id: int,
    document_file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> ProjectContextDocumentIngestResponse:
    _get_profile_row(profile_id, db)
    settings = get_settings()
    saved = await save_upload(document_file, settings, "project-context")
    try:
        text = extract_document_text(saved, settings)
    except (RuntimeError, ValueError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    filename = document_file.filename or saved.name
    return ProjectContextDocumentIngestResponse(
        filename=filename,
        extracted_text=text,
        char_count=len(text),
    )


@router.post("/profiles/{profile_id}/chat", response_model=ProjectContextChatResponse)
async def chat_with_profile_context(
    profile_id: int,
    body: ProjectContextChatRequest,
    db: Session = Depends(get_db),
) -> ProjectContextChatResponse:
    row = _get_profile_row(profile_id, db)
    package = InvestmentProjectPackage.model_validate(row.context_payload)
    settings = get_settings()
    instruction = (body.chat_prompt or "").strip() or DEFAULT_PROJECT_CONTEXT_CHAT_PROMPT
    ollama_prompt = build_project_context_chat_prompt(
        package=package,
        user_message=body.message,
        document_text=body.document_text,
        history=[turn.model_dump() for turn in body.history],
        instruction=instruction,
    )
    selected_model = (body.ollama_model or "").strip() or settings.ollama_model
    ollama = OllamaClient(settings)
    data = await ollama.chat_project_context(prompt=ollama_prompt, model=selected_model or None)

    if not data:
        return ProjectContextChatResponse(
            reply="Не удалось получить ответ от Ollama. Проверьте, что модель запущена локально.",
            changes_summary="",
            suggested_package=None,
            package_valid=False,
            ollama_model=selected_model,
            ollama_prompt=ollama_prompt,
        )

    reply = str(data.get("reply") or "").strip() or "Ответ модели пуст."
    changes_summary = str(data.get("changes_summary") or "").strip()
    raw_package = data.get("suggested_package")
    suggested: InvestmentProjectPackage | None = None
    package_valid = True
    if isinstance(raw_package, dict):
        try:
            suggested = InvestmentProjectPackage.model_validate(raw_package)
        except ValidationError:
            package_valid = False
            reply = (
                f"{reply}\n\nПредложенный пакет не прошёл валидацию схемы — примените правки вручную в JSON-редакторе."
            )

    return ProjectContextChatResponse(
        reply=reply,
        changes_summary=changes_summary,
        suggested_package=suggested,
        package_valid=package_valid,
        ollama_model=selected_model,
        ollama_prompt=ollama_prompt,
    )
