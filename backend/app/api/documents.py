import json
import shutil
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, Query, UploadFile
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.models import CheckStatus, DocumentComparison
from app.schemas import (
    BundleDeleteResponse,
    BundleDetailResponse,
    BundleListItem,
    BundlePdfUploadItem,
    BundleProjectContextResponse,
    DocumentBundleUploadResponse,
    DocumentComparisonResponse,
    PageComparison,
    RagIngestSummary,
)
from app.services.bundle_registry import (
    delete_bundle,
    find_batch_id_by_cipher,
    get_bundle_detail,
    list_bundle_pdf_paths,
    list_bundles,
    original_filenames_for_paths,
    write_initial_bundle_meta,
)
from app.services.bundle_project_context import (
    build_bundle_project_context,
    get_stored_bundle_project_context,
)
from app.services.rag_ingest import COLLECTION_LABEL, ingest_bundle_to_rag, resolve_rag_project_id
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


@router.get("/bundles", response_model=list[BundleListItem])
def list_document_bundles() -> list[BundleListItem]:
    """Дашборд: ранее загруженные комплекты и сводный статус конвейера."""
    return list_bundles(get_settings())


@router.get("/bundles/{batch_id}", response_model=BundleDetailResponse)
def get_document_bundle(batch_id: str) -> BundleDetailResponse:
    """Детальный просмотр комплекта и статусов RAG по каждому файлу."""
    detail = get_bundle_detail(get_settings(), batch_id)
    if detail is None:
        raise HTTPException(status_code=404, detail="Комплект не найден.")
    return detail


@router.delete("/bundles/{batch_id}", response_model=BundleDeleteResponse)
def delete_document_bundle(batch_id: str) -> BundleDeleteResponse:
    """Удаление комплекта: RAG (коллекция project_analysis) + локальные файлы."""
    deleted, rag_summary = delete_bundle(get_settings(), batch_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Комплект не найден.")
    return BundleDeleteResponse(batch_id=batch_id, local_deleted=True, rag=rag_summary)


@router.get("/bundles/{batch_id}/context", response_model=BundleProjectContextResponse)
def get_bundle_project_context(batch_id: str) -> BundleProjectContextResponse:
    """Сохранённый проектный контекст комплекта (после POST .../context/build)."""
    stored = get_stored_bundle_project_context(get_settings(), batch_id)
    if stored is None:
        raise HTTPException(
            status_code=404,
            detail="Контекст не собран. Вызовите POST /api/documents/bundles/{batch_id}/context/build.",
        )
    return stored


@router.post("/bundles/{batch_id}/context/build", response_model=BundleProjectContextResponse)
def build_bundle_project_context_endpoint(
    batch_id: str,
    max_tokens_per_document: int = Query(120, ge=20, le=500),
    max_excerpts: int = Query(48, ge=8, le=120),
    use_search: bool = Query(True, description="Дополнить контекст hybrid search по коллекции"),
) -> BundleProjectContextResponse:
    """Собрать проектный контекст из проиндексированных документов RAG и сохранить в bundle_meta."""
    settings = get_settings()
    try:
        return build_bundle_project_context(
            settings,
            batch_id,
            max_tokens_per_document=max_tokens_per_document,
            max_excerpts=max_excerpts,
            use_search=use_search,
            persist=True,
        )
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.post("/bundles/{batch_id}/rag/retry", response_model=RagIngestSummary)
def retry_bundle_rag_ingest(batch_id: str) -> RagIngestSummary:
    """Повторная отправка комплекта в RAG-конвейер (синхронно, с логами)."""
    settings = get_settings()
    pdf_paths = list_bundle_pdf_paths(settings, batch_id)
    if not pdf_paths:
        raise HTTPException(status_code=404, detail="Комплект или PDF не найдены.")

    meta_path = settings.storage_dir / "document_bundles" / batch_id / "bundle_meta.json"
    meta = {}
    if meta_path.exists():
        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            meta = {}

    name_map = original_filenames_for_paths(meta, pdf_paths)
    return ingest_bundle_to_rag(
        settings,
        pdf_paths=pdf_paths,
        project_cipher=meta.get("project_cipher"),
        batch_id=batch_id,
        bundle_meta_path=meta_path,
        original_filenames=name_map,
    )


@router.post("/bundles/rag/retry-by-cipher", response_model=RagIngestSummary)
def retry_bundle_rag_by_cipher(
    project_cipher: str = Query(..., description="Шифр проекта"),
) -> RagIngestSummary:
    """Перезапуск RAG по шифру проекта (напр. 3D01-0036-ТУГН.24.2144У-П-01)."""
    settings = get_settings()
    batch_id = find_batch_id_by_cipher(settings, project_cipher)
    if batch_id is None:
        raise HTTPException(
            status_code=404,
            detail=f"Комплект с шифром «{project_cipher}» не найден в document_bundles.",
        )
    return retry_bundle_rag_ingest(batch_id)


@router.post("/bundles/upload", response_model=DocumentBundleUploadResponse)
async def upload_document_bundle(
    background_tasks: BackgroundTasks,
    pdf_files: list[UploadFile] = File(..., description="Несколько PDF одного комплекта"),
    project_cipher: str | None = Form(None, description="Шифр проекта для привязки комплекта"),
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
    saved_paths: list[Path] = []
    original_name_map: dict[str, str] = {}
    manifest_lines: list[tuple[str, str]] = []
    try:
        for upload in pdf_files:
            path, size_bytes = await save_bundle_pdf(upload, settings, bundle_root)
            saved_paths.append(path)
            rel = path.relative_to(settings.storage_dir)
            rel_str = str(rel).replace("\\", "/")
            crc_hex = compute_file_crc32_hex(path)
            ukep = analyze_embedded_ukep_structural(path)
            manifest_lines.append((rel_str, crc_hex))
            original_name = upload.filename or path.name
            for key in (str(path), str(path.resolve()), path.name):
                original_name_map[key] = original_name
            items.append(
                BundlePdfUploadItem(
                    original_filename=original_name,
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

    cipher = (project_cipher or "").strip() or None
    meta_path = bundle_root / "bundle_meta.json"
    write_initial_bundle_meta(
        meta_path,
        batch_id=batch_id,
        project_cipher=cipher,
        total_files=len(items),
        bundle_manifest_crc32_hex=manifest_crc,
        overall_ukep_status=overall_ukep,
        files=[item.model_dump(mode="json") for item in items],
    )

    rag_summary: RagIngestSummary | None = None
    if settings.rag_enabled and saved_paths:

        def _rag_task() -> None:
            ingest_bundle_to_rag(
                settings,
                pdf_paths=saved_paths,
                project_cipher=cipher,
                batch_id=batch_id,
                bundle_meta_path=meta_path,
                original_filenames=original_name_map,
            )

        background_tasks.add_task(_rag_task)
        rag_summary = RagIngestSummary(
            enabled=True,
            status="queued",
            project_id=resolve_rag_project_id(cipher, batch_id),
            collection_label=COLLECTION_LABEL,
            collection_name=settings.rag_collection_project_analysis,
            documents_queued=len(saved_paths),
            message=(
                f"Комплект принят. {len(saved_paths)} PDF отправляются в RAG "
                f"(коллекция «{COLLECTION_LABEL}»): парсинг, токенизация, индексация."
            ),
        )

    return DocumentBundleUploadResponse(
        batch_id=batch_id,
        project_cipher=cipher,
        total_files=len(items),
        files=items,
        bundle_manifest_crc32_hex=manifest_crc,
        overall_ukep_status=overall_ukep,
        ukep_disclaimer=UKEP_STRUCTURAL_NOTE,
        rag_ingest=rag_summary,
    )


def _document_status(page_results: list[PageComparison]) -> str:
    if any(page.status == "Критично" for page in page_results):
        return "Критично"
    if any(page.status == "Требует проверки" for page in page_results):
        return "Требует проверки"
    return "OK"
