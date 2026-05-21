"""Реестр пакетов документов ИСМ."""

from __future__ import annotations

import json
import logging
import uuid
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx

from app.config import Settings
from app.services.bundle_registry import _fetch_document_status
from app.services.ism_extract import ISM_ALLOWED_SUFFIXES, extract_ism_text, is_ism_allowed_filename
from app.services.ism_interfaces import IsmInterfaceLink, detect_interfaces
from app.services.ism_rag import ISM_COLLECTION_LABEL, ingest_ism_package_to_rag
from app.services.ism_structured import IsmDocumentStructured, build_structured_document

logger = logging.getLogger(__name__)


def ism_packages_root(settings: Settings) -> Path:
    return settings.storage_dir / "ism_packages"


def package_dir(settings: Settings, package_id: str) -> Path:
    return ism_packages_root(settings) / package_id


def package_meta_path(settings: Settings, package_id: str) -> Path:
    return package_dir(settings, package_id) / "package_meta.json"


def read_package_meta(settings: Settings, package_id: str) -> dict[str, Any] | None:
    path = package_meta_path(settings, package_id)
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    return data if isinstance(data, dict) else None


def write_package_meta(settings: Settings, package_id: str, meta: dict[str, Any]) -> None:
    path = package_meta_path(settings, package_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")


def list_ism_packages(settings: Settings) -> list[dict[str, Any]]:
    root = ism_packages_root(settings)
    if not root.is_dir():
        return []
    items: list[dict[str, Any]] = []
    for pkg_dir in sorted(root.iterdir(), key=lambda p: p.stat().st_mtime, reverse=True):
        if not pkg_dir.is_dir():
            continue
        meta = read_package_meta(settings, pkg_dir.name)
        if not meta:
            continue
        items.append(_summary_from_meta(meta))
    return items


def _summary_from_meta(meta: dict[str, Any]) -> dict[str, Any]:
    docs = meta.get("documents") or []
    ifaces = meta.get("interfaces") or []
    rag = meta.get("rag_ingest") or {}
    indexed = sum(1 for d in docs if d.get("rag_job_status") == "indexed")
    return {
        "package_id": meta.get("package_id"),
        "project_cipher": meta.get("project_cipher"),
        "title": meta.get("title"),
        "total_files": len(docs),
        "documents_indexed": indexed,
        "interfaces_count": len(ifaces),
        "created_at": meta.get("created_at"),
        "pipeline_status": meta.get("pipeline_status", "accepted"),
        "pipeline_label": meta.get("pipeline_label", "Принят"),
        "rag_project_id": rag.get("project_id"),
    }


def process_uploaded_package(
    settings: Settings,
    *,
    saved_paths: list[tuple[Path, str]],
    project_cipher: str | None,
    title: str | None = None,
    run_rag: bool = True,
) -> dict[str, Any]:
    package_id = uuid.uuid4().hex
    pkg_dir = package_dir(settings, package_id)
    pkg_dir.mkdir(parents=True, exist_ok=True)

    documents: list[IsmDocumentStructured] = []
    full_texts: dict[str, str] = {}

    for path, rel in saved_paths:
        dest = pkg_dir / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        if path != dest:
            dest.write_bytes(path.read_bytes())

        parse_error: str | None = None
        text = ""
        try:
            text = extract_ism_text(dest, settings)
        except Exception as exc:
            parse_error = str(exc)
            logger.warning("ISM parse %s: %s", rel, exc)

        full_texts[Path(rel).name] = text
        doc = build_structured_document(
            dest,
            relative_path=rel,
            text=text,
            parse_error=parse_error,
        )
        documents.append(doc)

    interfaces = detect_interfaces(documents, full_texts)
    pipeline_status, pipeline_label = _pipeline_from_docs(documents)

    meta: dict[str, Any] = {
        "package_id": package_id,
        "project_cipher": (project_cipher or "").strip() or None,
        "title": (title or "").strip() or f"Пакет ИСМ {package_id[:8]}",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "pipeline_status": pipeline_status,
        "pipeline_label": pipeline_label,
        "documents": [_doc_to_dict(d) for d in documents],
        "interfaces": [_iface_to_dict(i) for i in interfaces],
        "structured_context": _build_structured_context(documents, interfaces),
        "rag_ingest": None,
    }

    if run_rag and settings.rag_enabled:
        rag_paths = [pkg_dir / d.relative_path for d in documents if d.parse_status != "failed"]
        summary = ingest_ism_package_to_rag(
            settings,
            file_paths=rag_paths,
            package_id=package_id,
            project_cipher=project_cipher,
            package_meta_path=package_meta_path(settings, package_id),
        )
        meta["rag_ingest"] = _rag_summary_dict(summary)
        _merge_rag_ids(meta, summary)

    write_package_meta(settings, package_id, meta)
    return get_package_detail(settings, package_id) or meta


def get_package_detail(settings: Settings, package_id: str) -> dict[str, Any] | None:
    meta = read_package_meta(settings, package_id)
    if not meta:
        return None
    _refresh_rag_statuses(settings, meta)
    pipeline_status, pipeline_label = _pipeline_from_docs_dict(meta.get("documents") or [])
    meta["pipeline_status"] = pipeline_status
    meta["pipeline_label"] = pipeline_label
    write_package_meta(settings, package_id, meta)
    return meta


def _refresh_rag_statuses(settings: Settings, meta: dict[str, Any]) -> None:
    if not settings.rag_enabled:
        return
    rag = meta.get("rag_ingest") or {}
    if not rag.get("project_id"):
        return
    base = settings.rag_api_url.rstrip("/")
    docs = meta.get("documents")
    if not isinstance(docs, list):
        return
    try:
        with httpx.Client(timeout=settings.rag_http_timeout_seconds, trust_env=False) as client:
            for row in docs:
                if not isinstance(row, dict):
                    continue
                doc_id = row.get("document_id")
                if not doc_id:
                    continue
                st = _fetch_document_status(client, base, str(doc_id))
                row["rag_job_status"] = st.get("job_status")
                row["tokens_count"] = int(st.get("tokens_count") or 0)
                if st.get("error"):
                    row["rag_error"] = st["error"]
    except httpx.HTTPError as exc:
        logger.warning("ISM RAG poll failed: %s", exc)


def retry_package_rag(settings: Settings, package_id: str) -> dict[str, Any]:
    meta = read_package_meta(settings, package_id)
    if not meta:
        raise ValueError("Пакет не найден.")
    pkg_dir = package_dir(settings, package_id)
    paths = []
    for row in meta.get("documents") or []:
        if isinstance(row, dict) and row.get("relative_path"):
            p = pkg_dir / str(row["relative_path"])
            if p.is_file():
                paths.append(p)
    summary = ingest_ism_package_to_rag(
        settings,
        file_paths=paths,
        package_id=package_id,
        project_cipher=meta.get("project_cipher"),
        package_meta_path=package_meta_path(settings, package_id),
    )
    meta["rag_ingest"] = _rag_summary_dict(summary)
    _merge_rag_ids(meta, summary)
    write_package_meta(settings, package_id, meta)
    return get_package_detail(settings, package_id) or meta


def _pipeline_from_docs(documents: list[IsmDocumentStructured]) -> tuple[str, str]:
    if not documents:
        return "accepted", "Пустой пакет"
    if all(d.parse_status == "failed" for d in documents):
        return "failed", "Ошибки разбора"
    if any(d.parse_status == "failed" for d in documents):
        return "partial", "Частичный разбор"
    return "parsed", "Структура извлечена"


def _pipeline_from_docs_dict(documents: list[Any]) -> tuple[str, str]:
    typed = [
        IsmDocumentStructured(
            filename=str(d.get("filename") or ""),
            relative_path=str(d.get("relative_path") or ""),
            file_type=str(d.get("file_type") or ""),
            size_bytes=int(d.get("size_bytes") or 0),
            discipline=d.get("discipline"),
            document_codes=list(d.get("document_codes") or []),
            section_hints=list(d.get("section_hints") or []),
            excerpt=str(d.get("excerpt") or ""),
            chars_extracted=int(d.get("chars_extracted") or 0),
            parse_status=str(d.get("parse_status") or "ok"),
            parse_error=d.get("parse_error"),
            document_id=d.get("document_id"),
            rag_job_status=d.get("rag_job_status"),
            tokens_count=int(d.get("tokens_count") or 0),
        )
        for d in documents
        if isinstance(d, dict)
    ]
    status, label = _pipeline_from_docs(typed)
    rag_indexed = sum(1 for d in typed if d.rag_job_status == "indexed")
    if rag_indexed and rag_indexed == len(typed):
        return "indexed", "Индексация в RAG завершена"
    if any(d.rag_job_status in {"parsing", "tokenizing", "embedding", "uploaded"} for d in typed):
        return "processing", "Конвейер RAG"
    if rag_indexed:
        return "partial", f"В RAG: {rag_indexed}/{len(typed)}"
    return status, label


def _build_structured_context(
    documents: list[IsmDocumentStructured],
    interfaces: list[IsmInterfaceLink],
) -> dict[str, Any]:
    disciplines = sorted({d.discipline for d in documents if d.discipline})
    codes = sorted({c for d in documents for c in d.document_codes})
    return {
        "collection_label": ISM_COLLECTION_LABEL,
        "documents_total": len(documents),
        "disciplines": disciplines,
        "document_codes": codes,
        "interfaces_total": len(interfaces),
        "resolved_interfaces": sum(1 for i in interfaces if i.target_filename),
    }


def _doc_to_dict(doc: IsmDocumentStructured) -> dict[str, Any]:
    return asdict(doc)


def _iface_to_dict(iface: IsmInterfaceLink) -> dict[str, Any]:
    return asdict(iface)


def _rag_summary_dict(summary: Any) -> dict[str, Any]:
    return {
        "enabled": summary.enabled,
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


def _merge_rag_ids(meta: dict[str, Any], summary: Any) -> None:
    by_name = {f.filename: f for f in summary.files}
    for row in meta.get("documents") or []:
        if not isinstance(row, dict):
            continue
        fr = by_name.get(row.get("filename"))
        if fr and fr.document_id:
            row["document_id"] = fr.document_id
            row["rag_job_status"] = "uploaded"
        if fr and fr.error:
            row["rag_error"] = fr.error
