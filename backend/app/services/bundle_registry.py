"""Реестр загруженных комплектов «Анализ проекта» и статус RAG-конвейера."""

from __future__ import annotations

import json
import logging
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx

from app.config import Settings
from app.schemas import (
    BundleDetailResponse,
    BundleListItem,
    BundlePipelineFileStatus,
    BundleRagIngestInfo,
    BundleStoredFile,
)
from app.services.rag_ingest import COLLECTION_LABEL, resolve_rag_project_id

logger = logging.getLogger(__name__)

_PIPELINE_ORDER = ("uploaded", "parsing", "tokenizing", "embedding", "indexed", "failed", "missing")

RAG_DOCUMENT_MISSING_MSG = (
    "Документ отсутствует в RAG (база пересоздана или запись удалена). "
    "Нажмите «Перезапустить RAG» в карточке комплекта."
)


def bundles_root(settings: Settings) -> Path:
    return settings.storage_dir / "document_bundles"


def bundle_meta_path(settings: Settings, batch_id: str) -> Path:
    return bundles_root(settings) / batch_id / "bundle_meta.json"


def read_bundle_meta(settings: Settings, batch_id: str) -> dict[str, Any] | None:
    return _read_meta(bundle_meta_path(settings, batch_id))


def write_bundle_meta(settings: Settings, batch_id: str, meta: dict[str, Any]) -> None:
    path = bundle_meta_path(settings, batch_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")


def find_batch_id_by_cipher(settings: Settings, project_cipher: str) -> str | None:
    cipher = project_cipher.strip()
    if not cipher:
        return None
    root = bundles_root(settings)
    if not root.is_dir():
        return None
    for batch_dir in root.iterdir():
        if not batch_dir.is_dir():
            continue
        meta = _read_meta(batch_dir / "bundle_meta.json")
        if meta and meta.get("project_cipher") == cipher:
            return batch_dir.name
    return None


def list_bundle_pdf_paths(settings: Settings, batch_id: str) -> list[Path]:
    batch_dir = bundles_root(settings) / batch_id
    if not batch_dir.is_dir():
        return []
    return sorted(batch_dir.glob("*.pdf"))


def build_original_filename_map(meta: dict[str, Any] | None) -> dict[str, str]:
    """Ключ: имя файла на диске (basename) → оригинальное имя из загрузки."""
    mapping: dict[str, str] = {}
    if not meta:
        return mapping
    for row in meta.get("files") or []:
        if not isinstance(row, dict):
            continue
        original = str(row.get("original_filename") or "").strip()
        if not original:
            continue
        rel = str(row.get("relative_path") or "")
        if rel:
            mapping[Path(rel).name] = original
        crc = str(row.get("crc32_hex") or "").upper()
        if crc:
            mapping[f"crc:{crc}"] = original
    return mapping


def display_filename_for_rag_row(
    rag_row: dict[str, Any],
    original_map: dict[str, str],
) -> str:
    disk_name = str(rag_row.get("filename") or "")
    crc = str(rag_row.get("crc32_hex") or "").upper()
    return (
        original_map.get(disk_name)
        or (original_map.get(f"crc:{crc}") if crc else None)
        or disk_name
        or "—"
    )


def original_filenames_for_paths(meta: dict[str, Any], pdf_paths: list[Path]) -> dict[str, str]:
    """Карта для RAG ingest: путь/имя на диске → оригинальное имя из bundle_meta."""
    by_disk = build_original_filename_map(meta)
    result: dict[str, str] = {}
    for path in pdf_paths:
        original = by_disk.get(path.name) or path.name
        result[str(path)] = original
        result[str(path.resolve())] = original
        result[path.name] = original
    return result


def collect_rag_document_ids(meta: dict[str, Any] | None) -> list[str]:
    """document_id из bundle_meta.rag_ingest.files."""
    if not meta:
        return []
    ids: list[str] = []
    for row in (meta.get("rag_ingest") or {}).get("files") or []:
        doc_id = row.get("document_id")
        if doc_id:
            ids.append(str(doc_id))
    return list(dict.fromkeys(ids))


def delete_bundle(settings: Settings, batch_id: str) -> tuple[bool, "RagDeleteSummary | None"]:
    """Удаляет комплект: сначала RAG (Qdrant/MinIO/БД), затем локальный каталог."""
    from app.services.rag_ingest import RagDeleteSummary, delete_documents_from_rag

    batch_dir = bundles_root(settings) / batch_id
    if not batch_dir.is_dir():
        return False, None

    meta = _read_meta(batch_dir / "bundle_meta.json")
    document_ids = collect_rag_document_ids(meta)

    rag_summary: RagDeleteSummary | None = None
    if document_ids:
        rag_summary = delete_documents_from_rag(settings, document_ids)

    shutil.rmtree(batch_dir)
    logger.info(
        "Удалён комплект batch_id=%s | rag_docs=%s",
        batch_id,
        rag_summary.documents_deleted if rag_summary else 0,
    )
    return True, rag_summary


def write_initial_bundle_meta(
    meta_path: Path,
    *,
    batch_id: str,
    project_cipher: str | None,
    total_files: int,
    bundle_manifest_crc32_hex: str,
    overall_ukep_status: str,
    files: list[dict[str, Any]],
) -> None:
    meta_path.write_text(
        json.dumps(
            {
                "batch_id": batch_id,
                "project_cipher": project_cipher,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "total_files": total_files,
                "bundle_manifest_crc32_hex": bundle_manifest_crc32_hex,
                "overall_ukep_status": overall_ukep_status,
                "files": files,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )


def list_bundles(settings: Settings) -> list[BundleListItem]:
    root = bundles_root(settings)
    if not root.is_dir():
        return []

    items: list[BundleListItem] = []
    for batch_dir in sorted(root.iterdir(), key=lambda p: p.stat().st_mtime, reverse=True):
        if not batch_dir.is_dir():
            continue
        batch_id = batch_dir.name
        meta = _read_meta(batch_dir / "bundle_meta.json")
        if meta is None:
            pdf_count = len(list(batch_dir.glob("*.pdf")))
            items.append(
                BundleListItem(
                    batch_id=batch_id,
                    project_cipher=None,
                    total_files=pdf_count,
                    created_at=datetime.fromtimestamp(batch_dir.stat().st_mtime, tz=timezone.utc),
                    overall_ukep_status="Требует проверки",
                    pipeline_status="accepted",
                    pipeline_label="Принят на сервере",
                    rag_project_id=None,
                )
            )
            continue

        file_statuses = _refresh_rag_file_statuses(settings, meta, batch_id=batch_id)
        pipeline_status, pipeline_label = _aggregate_pipeline(meta.get("rag_ingest"), file_statuses)
        items.append(
            BundleListItem(
                batch_id=batch_id,
                project_cipher=meta.get("project_cipher"),
                total_files=int(meta.get("total_files") or len(meta.get("files") or [])),
                created_at=_parse_dt(meta.get("created_at")) or datetime.fromtimestamp(
                    batch_dir.stat().st_mtime, tz=timezone.utc
                ),
                overall_ukep_status=str(meta.get("overall_ukep_status") or "Требует проверки"),
                pipeline_status=pipeline_status,
                pipeline_label=pipeline_label,
                rag_project_id=(meta.get("rag_ingest") or {}).get("project_id")
                or resolve_rag_project_id(meta.get("project_cipher"), batch_id),
            )
        )
    return items


def get_bundle_detail(settings: Settings, batch_id: str) -> BundleDetailResponse | None:
    batch_dir = bundles_root(settings) / batch_id
    if not batch_dir.is_dir():
        return None

    meta = _read_meta(batch_dir / "bundle_meta.json")
    if meta is None:
        pdfs = sorted(batch_dir.glob("*.pdf"))
        return BundleDetailResponse(
            batch_id=batch_id,
            project_cipher=None,
            total_files=len(pdfs),
            created_at=datetime.fromtimestamp(batch_dir.stat().st_mtime, tz=timezone.utc),
            overall_ukep_status="Требует проверки",
            bundle_manifest_crc32_hex="",
            pipeline_status="accepted",
            pipeline_label="Принят на сервере",
            files=[],
            rag_ingest=None,
            pipeline_files=[],
        )

    file_statuses = _refresh_rag_file_statuses(settings, meta, batch_id=batch_id)
    pipeline_status, pipeline_label = _aggregate_pipeline(meta.get("rag_ingest"), file_statuses)
    rag_raw = meta.get("rag_ingest")
    rag_info = None
    if rag_raw:
        rag_info = BundleRagIngestInfo(
            enabled=bool(rag_raw.get("enabled", True)),
            status=str(rag_raw.get("status", "")),
            project_id=rag_raw.get("project_id"),
            collection_label=str(rag_raw.get("collection_label") or COLLECTION_LABEL),
            collection_name=str(rag_raw.get("collection_name") or "project_analysis_text"),
            documents_queued=int(rag_raw.get("documents_queued") or 0),
            documents_failed=int(rag_raw.get("documents_failed") or 0),
            message=str(rag_raw.get("message") or ""),
        )

    stored_files: list[BundleStoredFile] = []
    for row in meta.get("files") or []:
        if not isinstance(row, dict):
            continue
        try:
            stored_files.append(BundleStoredFile.model_validate(row))
        except Exception:
            stored_files.append(
                BundleStoredFile(
                    original_filename=str(row.get("original_filename") or "—"),
                    size_bytes=int(row.get("size_bytes") or 0),
                    relative_path=str(row.get("relative_path") or ""),
                    crc32_hex=str(row.get("crc32_hex") or ""),
                    ukep=None,
                )
            )

    return BundleDetailResponse(
        batch_id=batch_id,
        project_cipher=meta.get("project_cipher"),
        total_files=int(meta.get("total_files") or len(stored_files)),
        created_at=_parse_dt(meta.get("created_at")) or datetime.fromtimestamp(
            batch_dir.stat().st_mtime, tz=timezone.utc
        ),
        overall_ukep_status=str(meta.get("overall_ukep_status") or "Требует проверки"),
        bundle_manifest_crc32_hex=str(meta.get("bundle_manifest_crc32_hex") or ""),
        pipeline_status=pipeline_status,
        pipeline_label=pipeline_label,
        files=stored_files,
        rag_ingest=rag_info,
        pipeline_files=file_statuses,
    )


def _read_meta(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    return data if isinstance(data, dict) else None


def _parse_dt(value: Any) -> datetime | None:
    if not value or not isinstance(value, str):
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _refresh_rag_file_statuses(
    settings: Settings,
    meta: dict[str, Any],
    *,
    batch_id: str | None = None,
) -> list[BundlePipelineFileStatus]:
    rag = meta.get("rag_ingest") or {}
    rag_files = rag.get("files") or []
    if not settings.rag_enabled or not rag_files:
        return []

    original_map = build_original_filename_map(meta)

    base = settings.rag_api_url.rstrip("/")
    results: list[BundlePipelineFileStatus] = []
    try:
        with httpx.Client(timeout=settings.rag_http_timeout_seconds, trust_env=False) as client:
            for row in rag_files:
                if not isinstance(row, dict):
                    continue
                filename = display_filename_for_rag_row(row, original_map)
                document_id = row.get("document_id")
                upload_error = row.get("error")
                if upload_error:
                    results.append(
                        BundlePipelineFileStatus(
                            filename=filename,
                            document_id=None,
                            job_status="failed",
                            job_stage=None,
                            tokens_count=0,
                            error=str(upload_error),
                        )
                    )
                    continue
                if not document_id:
                    results.append(
                        BundlePipelineFileStatus(
                            filename=filename,
                            document_id=None,
                            job_status="uploaded",
                            job_stage=None,
                            tokens_count=0,
                            error=None,
                        )
                    )
                    continue
                status = _fetch_document_status(client, base, str(document_id))
                results.append(
                    BundlePipelineFileStatus(
                        filename=filename,
                        document_id=str(document_id),
                        job_status=status.get("job_status", "uploaded"),
                        job_stage=status.get("job_stage"),
                        tokens_count=int(status.get("tokens_count") or 0),
                        error=status.get("error"),
                    )
                )
    except httpx.HTTPError as exc:
        logger.warning("RAG status poll failed: %s", exc)
        for row in rag_files:
            if isinstance(row, dict):
                results.append(
                    BundlePipelineFileStatus(
                        filename=str(row.get("filename") or ""),
                        document_id=row.get("document_id"),
                        job_status="unknown",
                        job_stage=None,
                        tokens_count=0,
                        error=f"RAG недоступна: {exc}",
                    )
                )
    if batch_id and results:
        _reconcile_missing_rag_documents_in_meta(settings, batch_id, meta, results)
    return results


def _reconcile_missing_rag_documents_in_meta(
    settings: Settings,
    batch_id: str,
    meta: dict[str, Any],
    statuses: list[BundlePipelineFileStatus],
) -> None:
    """Сбрасывает устаревшие document_id в bundle_meta после 404 от RAG API."""
    missing_ids = {f.document_id for f in statuses if f.job_status == "missing" and f.document_id}
    if not missing_ids:
        return
    rag = meta.get("rag_ingest")
    if not isinstance(rag, dict):
        return
    files = rag.get("files")
    if not isinstance(files, list):
        return
    changed = False
    for row in files:
        if not isinstance(row, dict):
            continue
        doc_id = row.get("document_id")
        if doc_id and str(doc_id) in missing_ids:
            row["stale_document_id"] = str(doc_id)
            row["document_id"] = None
            row["error"] = RAG_DOCUMENT_MISSING_MSG
            changed = True
    if changed:
        rag["status"] = "failed"
        rag["message"] = RAG_DOCUMENT_MISSING_MSG
        rag["last_error"] = RAG_DOCUMENT_MISSING_MSG
        write_bundle_meta(settings, batch_id, meta)
        logger.info(
            "batch=%s reconciled %s stale RAG document_id(s)",
            batch_id,
            len(missing_ids),
        )


def _fetch_document_status(client: httpx.Client, base: str, document_id: str) -> dict[str, Any]:
    try:
        response = client.get(f"{base}/documents/{document_id}/status")
        response.raise_for_status()
        payload = response.json()
        job = payload.get("job") or {}
        return {
            "job_status": job.get("status", "uploaded"),
            "job_stage": job.get("stage"),
            "tokens_count": payload.get("tokens_count", 0),
            "error": job.get("error_message"),
        }
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 404:
            return {
                "job_status": "missing",
                "job_stage": None,
                "tokens_count": 0,
                "error": RAG_DOCUMENT_MISSING_MSG,
            }
        return {
            "job_status": "unknown",
            "job_stage": None,
            "tokens_count": 0,
            "error": str(exc),
        }
    except httpx.HTTPError as exc:
        return {"job_status": "unknown", "job_stage": None, "tokens_count": 0, "error": str(exc)}


def _aggregate_pipeline(
    rag_ingest: Any,
    file_statuses: list[BundlePipelineFileStatus],
) -> tuple[str, str]:
    if not rag_ingest:
        return "accepted", "Принят (RAG не запускался)"

    rag_status = str((rag_ingest or {}).get("status") or "")
    if not file_statuses:
        rag_msg = str((rag_ingest or {}).get("message") or "")
        last_err = str((rag_ingest or {}).get("last_error") or "")
        labels = {
            "queued": ("queued", "В очереди RAG"),
            "in_progress": ("processing", "Отправка в RAG"),
            "failed": ("rag_failed", _short_label(last_err or rag_msg or "Ошибка RAG")),
            "partial": ("partial", _short_label(rag_msg or "Частичная отправка")),
            "skipped": ("accepted", "Только приёмка"),
        }
        return labels.get(rag_status, ("queued", "В очереди RAG"))

    statuses = [f.job_status for f in file_statuses]
    if any(s == "missing" for s in statuses):
        if any(s == "indexed" for s in statuses):
            return "partial", "Часть документов отсутствует в RAG"
        return "rag_failed", "Документы не найдены в RAG — перезапустите отправку"
    if statuses and all(s == "indexed" for s in statuses):
        return "indexed", "Индексация завершена"
    if any(s == "failed" for s in statuses):
        if any(s == "indexed" for s in statuses):
            return "partial", "Частично проиндексирован"
        return "failed", "Ошибки конвейера"
    if any(s in {"parsing", "tokenizing", "embedding", "uploaded"} for s in statuses):
        return "processing", "Конвейер RAG"
    return "processing", "Обработка"


def _short_label(text: str, max_len: int = 80) -> str:
    one_line = " ".join(text.split())
    return one_line if len(one_line) <= max_len else one_line[: max_len - 1] + "…"
