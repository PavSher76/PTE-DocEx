from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.models import CheckStatus, CorrespondenceCheck
from app.schemas import CorrespondenceRequest, CorrespondenceResponse, LanguageIssue, StyleAssessment
from app.services.correspondence_prompt import (
    DEFAULT_CORRESPONDENCE_PROMPT,
    build_correspondence_prompt,
    build_languagetool_report,
)
from app.services.languagetool import LanguageToolClient
from app.services.ollama import OllamaClient
from app.services.pdf_text import extract_pdf_text
from app.services.storage import save_upload

router = APIRouter(prefix="/correspondence", tags=["correspondence"])


@router.post("/check", response_model=CorrespondenceResponse)
async def check_correspondence(
    request: CorrespondenceRequest,
    db: Session = Depends(get_db),
) -> CorrespondenceResponse:
    terminology = request.terminology
    return await _check_text(
        text=request.text,
        terminology=terminology,
        check_prompt=request.check_prompt or DEFAULT_CORRESPONDENCE_PROMPT,
        business_context=request.business_context or "",
        strictness=request.strictness,
        db=db,
    )


@router.post("/check-pdf", response_model=CorrespondenceResponse)
async def check_correspondence_pdf(
    pdf_file: UploadFile = File(...),
    terminology: str = Form(""),
    check_prompt: str = Form(DEFAULT_CORRESPONDENCE_PROMPT),
    business_context: str = Form(""),
    strictness: str = Form("standard"),
    db: Session = Depends(get_db),
) -> CorrespondenceResponse:
    settings = get_settings()
    pdf_path = await save_upload(pdf_file, settings, "correspondence")
    try:
        extracted = extract_pdf_text(pdf_path, settings)
    except (RuntimeError, ValueError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    terms = [item.strip() for item in terminology.splitlines() if item.strip()]
    return await _check_text(
        text=extracted.text,
        terminology=terms,
        check_prompt=check_prompt,
        business_context=business_context,
        strictness=_normalize_strictness(strictness),
        db=db,
    )


async def _check_text(
    *,
    text: str,
    terminology: list[str],
    check_prompt: str,
    business_context: str,
    strictness: str,
    db: Session,
) -> CorrespondenceResponse:
    settings = get_settings()
    language_tool = LanguageToolClient(settings)
    ollama = OllamaClient(settings)

    lt_matches = await language_tool.check(text)
    languagetool_report = build_languagetool_report(text, lt_matches)
    ollama_prompt = build_correspondence_prompt(
        check_prompt=check_prompt,
        letter_text=text,
        terminology=terminology,
        business_context=business_context,
        strictness=strictness,
        languagetool_report=languagetool_report,
    )
    filtered_matches, style_assessment = await ollama.analyze_correspondence(
        prompt=ollama_prompt,
        issues=lt_matches,
    )
    status = _overall_status(filtered_matches, style_assessment)

    record = CorrespondenceCheck(
        source_text=text,
        status=CheckStatus(status),
        language_tool_matches=[issue.model_dump() for issue in lt_matches],
        filtered_matches=[issue.model_dump() for issue in filtered_matches],
        style_assessment=style_assessment.model_dump(),
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return CorrespondenceResponse(
        id=record.id,
        status=record.status.value,
        source_text=record.source_text,
        languagetool_report=languagetool_report,
        ollama_prompt=ollama_prompt,
        language_tool_matches=[LanguageIssue.model_validate(issue) for issue in record.language_tool_matches],
        filtered_matches=[LanguageIssue.model_validate(issue) for issue in record.filtered_matches],
        style_assessment=StyleAssessment.model_validate(record.style_assessment),
        created_at=record.created_at,
    )


def _overall_status(issues: list[LanguageIssue], style_assessment: StyleAssessment) -> str:
    if any(issue.severity == "critical" for issue in issues) or style_assessment.status == "Критично":
        return "Критично"
    if issues or style_assessment.status == "Требует проверки":
        return "Требует проверки"
    return "OK"


def _normalize_strictness(strictness: str) -> str:
    if strictness in {"standard", "strict", "critical"}:
        return strictness
    return "standard"
