from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.models import CheckStatus, DocumentComparison
from app.schemas import DocumentComparisonResponse, PageComparison
from app.services.document_compare import DocumentComparisonService
from app.services.storage import save_upload

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/compare", response_model=DocumentComparisonResponse)
async def compare_documents(
    pdf_file: UploadFile = File(...),
    editable_file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> DocumentComparisonResponse:
    settings = get_settings()
    pdf_path = await save_upload(pdf_file, settings, "documents")
    editable_path = await save_upload(editable_file, settings, "documents")
    service = DocumentComparisonService(settings)

    try:
        similarity, page_results, conclusion = service.compare(pdf_path, editable_path)
    except (RuntimeError, ValueError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    status = _document_status(page_results)
    record = DocumentComparison(
        pdf_filename=pdf_file.filename or pdf_path.name,
        editable_filename=editable_file.filename or editable_path.name,
        status=CheckStatus(status),
        similarity=similarity,
        conclusion=conclusion,
        page_results=[page.model_dump() for page in page_results],
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return DocumentComparisonResponse(
        id=record.id,
        status=record.status.value,
        similarity=record.similarity,
        conclusion=record.conclusion,
        page_results=[PageComparison.model_validate(page) for page in record.page_results],
        created_at=record.created_at,
    )


def _document_status(page_results: list[PageComparison]) -> str:
    if any(page.status == "Критично" for page in page_results):
        return "Критично"
    if any(page.status == "Требует проверки" for page in page_results):
        return "Требует проверки"
    return "OK"
