import shutil
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.models import CheckStatus, DocumentComparison
from app.schemas import (
    BundlePdfUploadItem,
    DocumentBundleUploadResponse,
    DocumentComparisonResponse,
    PageComparison,
)
from app.services.document_compare import DocumentComparisonService
from app.services.pdf_bundle_validation import (
    UKEP_STRUCTURAL_NOTE,
    analyze_embedded_ukep_structural,
    compute_bundle_manifest_crc32_hex,
    compute_file_crc32_hex,
    worst_status,
)
from app.services.storage import save_bundle_pdf, save_upload

router = APIRouter(prefix="/documents", tags=["documents"])

_MAX_FILES_PER_BUNDLE = 100


def _is_pdf_upload(upload: UploadFile) -> bool:
    name = (upload.filename or "").lower()
    if name.endswith(".pdf"):
        return True
    ctype = (upload.content_type or "").lower()
    return ctype in {"application/pdf", "application/x-pdf"}


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


@router.post("/bundles/upload", response_model=DocumentBundleUploadResponse)
async def upload_document_bundle(
    pdf_files: list[UploadFile] = File(..., description="Несколько PDF одного комплекта"),
) -> DocumentBundleUploadResponse:
    """Пакетная приёмка PDF комплекта (ПД/РД): сохранение на диск с группировкой по batch_id."""
    settings = get_settings()
    if not pdf_files:
        raise HTTPException(status_code=422, detail="Добавьте хотя бы один PDF-файл.")
    if len(pdf_files) > _MAX_FILES_PER_BUNDLE:
        raise HTTPException(
            status_code=422,
            detail=f"За один запрос можно загрузить не более {_MAX_FILES_PER_BUNDLE} файлов.",
        )

    for upload in pdf_files:
        if not _is_pdf_upload(upload):
            label = upload.filename or "без имени"
            raise HTTPException(
                status_code=422,
                detail=f"Файл «{label}» не распознан как PDF. Принимаются только файлы с расширением .pdf.",
            )

    batch_id = uuid4().hex
    bundle_root = settings.storage_dir / "document_bundles" / batch_id
    bundle_root.mkdir(parents=True, exist_ok=False)

    items: list[BundlePdfUploadItem] = []
    manifest_lines: list[tuple[str, str]] = []
    try:
        for upload in pdf_files:
            path, size_bytes = await save_bundle_pdf(upload, settings, bundle_root)
            rel = path.relative_to(settings.storage_dir)
            rel_str = str(rel).replace("\\", "/")
            crc_hex = compute_file_crc32_hex(path)
            ukep = analyze_embedded_ukep_structural(path)
            manifest_lines.append((rel_str, crc_hex))
            items.append(
                BundlePdfUploadItem(
                    original_filename=upload.filename or path.name,
                    size_bytes=size_bytes,
                    relative_path=rel_str,
                    crc32_hex=crc_hex,
                    ukep=ukep,
                )
            )
    except HTTPException:
        shutil.rmtree(bundle_root, ignore_errors=True)
        raise
    except Exception:
        shutil.rmtree(bundle_root, ignore_errors=True)
        raise

    manifest_crc = compute_bundle_manifest_crc32_hex(manifest_lines)
    overall_ukep = worst_status([item.ukep.status for item in items])

    return DocumentBundleUploadResponse(
        batch_id=batch_id,
        total_files=len(items),
        files=items,
        bundle_manifest_crc32_hex=manifest_crc,
        overall_ukep_status=overall_ukep,
        ukep_disclaimer=UKEP_STRUCTURAL_NOTE,
    )


def _document_status(page_results: list[PageComparison]) -> str:
    if any(page.status == "Критично" for page in page_results):
        return "Критично"
    if any(page.status == "Требует проверки" for page in page_results):
        return "Требует проверки"
    return "OK"
