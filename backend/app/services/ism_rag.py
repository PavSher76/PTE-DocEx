"""Отправка пакета ИСМ в RAG Platform."""

from __future__ import annotations

import logging
import mimetypes
import time
from pathlib import Path

import httpx

from app.config import Settings
from app.services.rag_ingest import (
    RagIngestFileResult,
    RagIngestSummary,
    _http_error_detail,
    _ping_rag,
    _write_rag_meta,
    resolve_rag_project_id,
)

logger = logging.getLogger("rag.ingest.ism")

RAG_COLLECTION_ISM = "ism"
ISM_COLLECTION_LABEL = "Документы ИСМ"


def _content_type(path: Path) -> str:
    guessed, _ = mimetypes.guess_type(path.name)
    if guessed:
        return guessed
    suffix = path.suffix.lower()
    return {
        ".pdf": "application/pdf",
        ".doc": "application/msword",
        ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ".xls": "application/vnd.ms-excel",
        ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    }.get(suffix, "application/octet-stream")


def ingest_ism_package_to_rag(
    settings: Settings,
    *,
    file_paths: list[Path],
    package_id: str,
    project_cipher: str | None,
    package_meta_path: Path | None = None,
) -> RagIngestSummary:
    if not settings.rag_enabled:
        return RagIngestSummary(
            enabled=False,
            status="skipped",
            message="RAG отключён (RAG_ENABLED=false).",
        )

    base = settings.rag_api_url.rstrip("/")
    project_id = resolve_rag_project_id(project_cipher, package_id)
    if not project_id.startswith("ISM-"):
        project_id = f"ISM-{project_id}"

    summary = RagIngestSummary(
        enabled=True,
        status="in_progress",
        project_id=project_id,
        collection_label=ISM_COLLECTION_LABEL,
        collection_name=getattr(settings, "rag_collection_ism", "ism_documents_text"),
    )
    t0 = time.perf_counter()
    logger.info("▶ ISM RAG ingest package=%s | files=%s", package_id, len(file_paths))

    try:
        with httpx.Client(timeout=settings.rag_http_timeout_seconds, trust_env=False) as client:
            _ping_rag(client, base, package_id)
            _ensure_ism_rag_project(client, base, project_id, project_cipher, package_id)
            for path in file_paths:
                result = _upload_ism_file(client, base, project_id, path, settings, package_id)
                summary.files.append(result)
                if result.error:
                    summary.documents_failed += 1
                else:
                    summary.documents_queued += 1
    except httpx.HTTPError as exc:
        detail = _http_error_detail(exc)
        summary.status = "failed"
        summary.last_error = detail
        summary.message = f"RAG Platform недоступна ({base}): {detail}"
        _write_rag_meta(package_meta_path, summary)
        return summary

    if summary.documents_failed and summary.documents_queued:
        summary.status = "partial"
        summary.message = (
            f"Часть файлов отправлена в RAG («{ISM_COLLECTION_LABEL}»): "
            f"{summary.documents_queued} ок, {summary.documents_failed} с ошибками."
        )
    elif summary.documents_failed:
        summary.status = "failed"
        summary.message = "Не удалось отправить документы ИСМ в RAG."
    else:
        summary.status = "queued"
        summary.message = (
            f"{summary.documents_queued} документов в очереди RAG («{ISM_COLLECTION_LABEL}»)."
        )

    logger.info(
        "✓ ISM RAG package=%s | ok=%s fail=%s | %.1fs",
        package_id,
        summary.documents_queued,
        summary.documents_failed,
        time.perf_counter() - t0,
    )
    _write_rag_meta(package_meta_path, summary)
    return summary


def _ensure_ism_rag_project(
    client: httpx.Client,
    base: str,
    project_id: str,
    project_cipher: str | None,
    package_id: str,
) -> None:
    title = project_cipher or f"ИСМ {package_id[:8]}"
    listed = client.get(f"{base}/projects")
    listed.raise_for_status()
    for row in listed.json():
        if row.get("project_id") == project_id:
            return
    created = client.post(
        f"{base}/projects",
        json={
            "project_id": project_id,
            "name": f"Документы ИСМ — {title}",
            "description": "Пакет документов ИСМ (DOC/XLS/PDF) из PTE-DocEx.",
        },
    )
    if created.status_code != 409:
        created.raise_for_status()


def _upload_ism_file(
    client: httpx.Client,
    base: str,
    project_id: str,
    path: Path,
    settings: Settings,
    package_id: str,
) -> RagIngestFileResult:
    name = path.name
    try:
        data = path.read_bytes()
        if len(data) > settings.max_upload_mb * 1024 * 1024:
            return RagIngestFileResult(
                filename=name,
                error=f"Файл больше {settings.max_upload_mb} МБ.",
            )
        response = client.post(
            f"{base}/documents/upload",
            data={
                "project_id": project_id,
                "rag_collection": RAG_COLLECTION_ISM,
                "discipline": _discipline_from_name(name),
            },
            files={"file": (name, data, _content_type(path))},
        )
        response.raise_for_status()
        payload = response.json()
        return RagIngestFileResult(
            filename=name,
            document_id=str(payload.get("document_id", "")),
            job_id=str(payload.get("job_id", "")),
        )
    except httpx.HTTPError as exc:
        return RagIngestFileResult(filename=name, error=_http_error_detail(exc))


def _discipline_from_name(filename: str) -> str | None:
    import re

    m = re.search(
        r"(?:^|[_\-\s])(АР|КР|КЖ|ОВ|ВК|ЭО|ТХ|СС|ПОС|ГП|ПЗ|ИОС|АС|ТМ)(?:[_\-\s.]|$)",
        filename,
        re.IGNORECASE,
    )
    return m.group(1).upper() if m else None
