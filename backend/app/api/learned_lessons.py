from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.config import get_settings
from app.schemas import LearnedLessonsAnalyzeResponse, OllamaModelsResponse
from app.services.learned_lessons_parser import parse_learned_lessons_workbook
from app.services.learned_lessons_prompt import (
    DEFAULT_LEARNED_LESSONS_PROMPT,
    build_learned_lessons_prompt,
)
from app.services.ollama import OllamaClient
from app.services.storage import save_upload

router = APIRouter(prefix="/learned-lessons", tags=["learned-lessons"])

ALLOWED_EXTENSIONS = {".xlsm", ".xlsx", ".xls"}


@router.get("/models", response_model=OllamaModelsResponse)
async def list_ollama_models() -> OllamaModelsResponse:
    settings = get_settings()
    result = await OllamaClient(settings).list_models()
    return OllamaModelsResponse(
        models=result.models,
        default_model=settings.ollama_model,
        ollama_reachable=result.error is None,
        error=result.error,
    )


@router.post("/analyze", response_model=LearnedLessonsAnalyzeResponse)
async def analyze_learned_lessons_workbook(
    excel_file: UploadFile = File(...),
    analysis_prompt: str = Form(DEFAULT_LEARNED_LESSONS_PROMPT),
    ollama_model: str = Form(""),
) -> LearnedLessonsAnalyzeResponse:
    settings = get_settings()
    filename = (excel_file.filename or "").lower()
    if not any(filename.endswith(ext) for ext in ALLOWED_EXTENSIONS):
        raise HTTPException(
            status_code=422,
            detail="Ожидается файл Excel: .xlsm, .xlsx или .xls",
        )

    saved_path = await save_upload(excel_file, settings, "learned_lessons")
    try:
        parsed_data = parse_learned_lessons_workbook(saved_path)
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"Не удалось разобрать форму: {exc}") from exc

    if not parsed_data.get("lessons"):
        raise HTTPException(
            status_code=422,
            detail="В файле не найдены строки выученных уроков. Проверьте лист «Форма для подготовки к сессии».",
        )

    ollama_prompt = build_learned_lessons_prompt(
        analysis_prompt=analysis_prompt,
        session_data=parsed_data,
    )
    selected_model = ollama_model.strip() or settings.ollama_model
    analysis = await OllamaClient(settings).analyze_learned_lessons(
        prompt=ollama_prompt,
        model=selected_model,
    )
    status = _analysis_status(analysis)

    return LearnedLessonsAnalyzeResponse(
        parsed_data=parsed_data,
        ollama_prompt=ollama_prompt,
        ollama_model=selected_model,
        analysis=analysis,
        status=status,
    )


def _analysis_status(analysis) -> str:
    if analysis.root_causes:
        return "OK"
    return "Требует проверки"
