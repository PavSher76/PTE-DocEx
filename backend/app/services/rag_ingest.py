"""Отправка комплекта PDF из «Анализ проекта» в RAG Platform."""

from __future__ import annotations

import json
import logging
import re
import time
from dataclasses import dataclass, field
from pathlib import Path

import httpx

from app.config import Settings

logger = logging.getLogger("rag.ingest")

RAG_COLLECTION_TAG = "project_analysis"
COLLECTION_LABEL = "Анализ проекта"


@dataclass
class RagIngestFileResult:
    filename: str
    document_id: str | None = None
    job_id: str | None = None
    error: str | None = None


@dataclass
class RagDeleteFileResult:
    document_id: str
    deleted: bool
    error: str | None = None


@dataclass
class RagDeleteSummary:
    enabled: bool
    documents_requested: int = 0
    documents_deleted: int = 0
    files: list[RagDeleteFileResult] = field(default_factory=list)
    message: str = ""


@dataclass
class RagIngestSummary:
    enabled: bool
    status: str
    project_id: str | None = None
    collection_label: str = COLLECTION_LABEL
    collection_name: str = "project_analysis_text"
    documents_queued: int = 0
    documents_failed: int = 0
    files: list[RagIngestFileResult] = field(default_factory=list)
    message: str = ""
    last_error: str | None = None


def resolve_rag_project_id(project_cipher: str | None, batch_id: str) -> str:
    raw = (project_cipher or "").strip()
    if raw:
        cleaned = re.sub(r"[^\w.\-]+", "-", raw, flags=re.UNICODE)
        return cleaned[:64].strip("-") or f"ANALIZ-{batch_id[:12]}"
    return f"ANALIZ-{batch_id[:12]}"


def _http_error_detail(exc: httpx.HTTPError) -> str:
    if isinstance(exc, httpx.HTTPStatusError):
        body = (exc.response.text or "").strip()[:800]
        return f"HTTP {exc.response.status_code}: {body or exc.response.reason_phrase}"
    return str(exc)


def resolve_upload_display_name(
    path: Path,
    original_filenames: dict[str, str] | None,
) -> str:
    """Имя для UI/RAG: original_filenames по полному пути или basename на диске."""
    if not original_filenames:
        return path.name
    return (
        original_filenames.get(str(path.resolve()))
        or original_filenames.get(str(path))
        or original_filenames.get(path.name)
        or path.name
    )


def ingest_bundle_to_rag(
    settings: Settings,
    *,
    pdf_paths: list[Path],
    project_cipher: str | None,
    batch_id: str,
    bundle_meta_path: Path | None = None,
    original_filenames: dict[str, str] | None = None,
) -> RagIngestSummary:
    t0 = time.perf_counter()
    if not settings.rag_enabled:
        logger.info("batch=%s RAG отключён (RAG_ENABLED=false)", batch_id)
        return RagIngestSummary(
            enabled=False,
            status="skipped",
            message="RAG отключён (RAG_ENABLED=false).",
        )

    base = settings.rag_api_url.rstrip("/")
    project_id = resolve_rag_project_id(project_cipher, batch_id)
    summary = RagIngestSummary(
        enabled=True,
        status="in_progress",
        project_id=project_id,
        collection_name=settings.rag_collection_project_analysis,
    )

    logger.info(
        "▶ RAG ingest batch=%s | cipher=%s | rag_project=%s | files=%s | api=%s",
        batch_id,
        project_cipher or "—",
        project_id,
        len(pdf_paths),
        base,
    )

    try:
        with httpx.Client(timeout=settings.rag_http_timeout_seconds, trust_env=False) as client:
            _ping_rag(client, base, batch_id)
            _ensure_rag_project(client, base, project_id, project_cipher, batch_id)
            for path in pdf_paths:
                result = _upload_pdf(
                    client,
                    base,
                    project_id,
                    path,
                    settings,
                    batch_id,
                    display_name=resolve_upload_display_name(path, original_filenames),
                )
                summary.files.append(result)
                if result.error:
                    summary.documents_failed += 1
                else:
                    summary.documents_queued += 1
    except httpx.HTTPError as exc:
        detail = _http_error_detail(exc)
        logger.error("✗ RAG ingest batch=%s | %s", batch_id, detail)
        summary.status = "failed"
        summary.last_error = detail
        summary.message = f"RAG Platform недоступна ({base}): {detail}"
        _write_rag_meta(bundle_meta_path, summary)
        return summary

    if summary.documents_failed and summary.documents_queued:
        summary.status = "partial"
        summary.message = (
            f"В коллекцию «{COLLECTION_LABEL}» поставлено в очередь {summary.documents_queued} "
            f"из {len(pdf_paths)} файлов (разборка и токенизация в worker)."
        )
    elif summary.documents_failed:
        summary.status = "failed"
        summary.last_error = summary.files[0].error if summary.files else "upload failed"
        summary.message = f"Не удалось отправить файлы в RAG. {summary.last_error or ''}".strip()
    else:
        summary.status = "queued"
        summary.message = (
            f"{summary.documents_queued} PDF отправлены в RAG («{COLLECTION_LABEL}»). "
            "Идёт парсинг, инженерная токенизация и индексация."
        )

    logger.info(
        "✓ RAG ingest batch=%s | status=%s | ok=%s fail=%s | %.1fs",
        batch_id,
        summary.status,
        summary.documents_queued,
        summary.documents_failed,
        time.perf_counter() - t0,
    )
    _write_rag_meta(bundle_meta_path, summary)
    return summary


def _ping_rag(client: httpx.Client, base: str, batch_id: str) -> None:
    try:
        response = client.get(f"{base}/health", timeout=10.0)
        response.raise_for_status()
        logger.info("batch=%s RAG health OK: %s", batch_id, response.json())
    except httpx.HTTPError as exc:
        raise httpx.ConnectError(f"health check failed: {_http_error_detail(exc)}") from exc


def _ensure_rag_project(
    client: httpx.Client,
    base: str,
    project_id: str,
    project_cipher: str | None,
    batch_id: str,
) -> None:
    logger.info("batch=%s проверка проекта RAG: %s", batch_id, project_id)
    listed = client.get(f"{base}/projects")
    listed.raise_for_status()
    for row in listed.json():
        if row.get("project_id") == project_id:
            logger.info("batch=%s проект RAG уже есть: %s", batch_id, project_id)
            return

    title = project_cipher or f"Анализ проекта {batch_id[:8]}"
    created = client.post(
        f"{base}/projects",
        json={
            "project_id": project_id,
            "name": f"Анализ проекта — {title}",
            "description": "Комплект ПД/РД из раздела «Анализ проекта» (PTE-DocEx).",
        },
    )
    if created.status_code == 409:
        logger.info("batch=%s проект RAG 409 (уже создан): %s", batch_id, project_id)
        return
    created.raise_for_status()
    logger.info("batch=%s создан проект RAG: %s", batch_id, project_id)


def _upload_pdf(
    client: httpx.Client,
    base: str,
    project_id: str,
    path: Path,
    settings: Settings,
    batch_id: str,
    *,
    display_name: str | None = None,
) -> RagIngestFileResult:
    name = display_name or path.name
    try:
        data = path.read_bytes()
        size_mb = len(data) / (1024 * 1024)
        if len(data) > settings.max_upload_mb * 1024 * 1024:
            msg = f"Файл больше {settings.max_upload_mb} МБ — пропущен для RAG."
            logger.warning("batch=%s %s: %s", batch_id, name, msg)
            return RagIngestFileResult(filename=name, error=msg)

        logger.info("batch=%s upload → %s (%.1f МБ)", batch_id, name, size_mb)
        response = client.post(
            f"{base}/documents/upload",
            data={
                "project_id": project_id,
                "rag_collection": RAG_COLLECTION_TAG,
            },
            files={"file": (name, data, "application/pdf")},
        )
        response.raise_for_status()
        payload = response.json()
        doc_id = str(payload.get("document_id", ""))
        job_id = str(payload.get("job_id", ""))
        logger.info(
            "batch=%s ✓ %s → document_id=%s job_id=%s status=%s",
            batch_id,
            name,
            doc_id[:8] if doc_id else "—",
            job_id[:8] if job_id else "—",
            payload.get("status"),
        )
        return RagIngestFileResult(filename=name, document_id=doc_id, job_id=job_id)
    except httpx.HTTPError as exc:
        detail = _http_error_detail(exc)
        logger.error("batch=%s ✗ upload %s | %s", batch_id, name, detail)
        return RagIngestFileResult(filename=name, error=detail)


def _write_rag_meta(bundle_meta_path: Path | None, summary: RagIngestSummary) -> None:
    if bundle_meta_path is None or not bundle_meta_path.exists():
        return
    try:
        meta = json.loads(bundle_meta_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        meta = {}
    meta["rag_ingest"] = {
        "status": summary.status,
        "project_id": summary.project_id,
        "collection_label": summary.collection_label,
        "collection_name": summary.collection_name,
        "documents_queued": summary.documents_queued,
        "documents_failed": summary.documents_failed,
        "message": summary.message,
        "last_error": summary.last_error,
        "files": [
            {
                "filename": f.filename,
                "document_id": f.document_id,
                "job_id": f.job_id,
                "error": f.error,
            }
            for f in summary.files
        ],
    }
    bundle_meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")


def delete_documents_from_rag(settings: Settings, document_ids: list[str]) -> RagDeleteSummary:
    """Удаляет документы комплекта из RAG Platform (Qdrant, MinIO, PostgreSQL)."""
    unique_ids = [d for d in dict.fromkeys(document_ids) if d and str(d).strip()]
    if not settings.rag_enabled:
        return RagDeleteSummary(
            enabled=False,
            message="RAG отключён (RAG_ENABLED=false).",
        )
    if not unique_ids:
        return RagDeleteSummary(
            enabled=True,
            message="Нет document_id для удаления в RAG.",
        )

    base = settings.rag_api_url.rstrip("/")
    summary = RagDeleteSummary(
        enabled=True,
        documents_requested=len(unique_ids),
    )
    logger.info("▶ RAG delete | documents=%s | api=%s", len(unique_ids), base)

    try:
        with httpx.Client(timeout=settings.rag_http_timeout_seconds, trust_env=False) as client:
            client.get(f"{base}/health", timeout=10.0).raise_for_status()
            for doc_id in unique_ids:
                result = RagDeleteFileResult(document_id=doc_id, deleted=False)
                try:
                    response = client.delete(f"{base}/documents/{doc_id}")
                    if response.status_code == 404:
                        result.deleted = True
                        result.error = "уже отсутствует в RAG"
                        summary.documents_deleted += 1
                    else:
                        response.raise_for_status()
                        result.deleted = True
                        summary.documents_deleted += 1
                        logger.info("✓ RAG delete document_id=%s", doc_id[:8])
                except httpx.HTTPError as exc:
                    result.error = _http_error_detail(exc)
                    logger.error("✗ RAG delete document_id=%s | %s", doc_id[:8], result.error)
                summary.files.append(result)
    except httpx.HTTPError as exc:
        detail = _http_error_detail(exc)
        logger.error("✗ RAG delete batch | %s", detail)
        return RagDeleteSummary(
            enabled=True,
            documents_requested=len(unique_ids),
            message=f"RAG Platform недоступна ({base}): {detail}",
        )

    failed = summary.documents_requested - summary.documents_deleted
    if failed:
        summary.message = (
            f"Удалено из RAG {summary.documents_deleted} из {summary.documents_requested} документов."
        )
    else:
        summary.message = f"Все {summary.documents_deleted} документов удалены из коллекции «{COLLECTION_LABEL}»."
    return summary
