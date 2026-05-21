"""Построение проектного контекста из проиндексированного комплекта (RAG tokens + search)."""

from __future__ import annotations

import json
import logging
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

import httpx

from app.config import Settings
from app.schemas import (
    BundleContextDocumentSummary,
    BundleContextExcerpt,
    BundleContextStructured,
    BundleProjectContextResponse,
)
from app.services.bundle_registry import (
    RAG_DOCUMENT_MISSING_MSG,
    get_bundle_detail,
    read_bundle_meta,
    write_bundle_meta,
)
from app.services.rag_ingest import COLLECTION_LABEL

logger = logging.getLogger(__name__)

_ELEMENT_PRIORITY = {
    "title_sheet": 0,
    "title": 1,
    "section": 2,
    "subsection": 3,
    "requirement": 4,
    "specification": 5,
    "document_register": 6,
    "volume_index": 7,
    "note": 8,
    "text": 9,
    "table": 10,
    "calculation": 11,
    "stamp": 12,
    "drawing_zone": 13,
    "drawing_sheet": 14,
}

_SEED_SEARCH_QUERIES = (
    "общие сведения о проекте назначение объекта",
    "исходные данные и исходно-разрешительная документация",
    "основные технические решения и параметры",
    "требования к проектированию и состав проектной документации",
)


@dataclass
class _BuildOptions:
    max_tokens_per_document: int = 120
    max_excerpts: int = 48
    use_search: bool = True
    search_top_k: int = 8


@dataclass
class _TokenRow:
    text: str
    element_type: str
    page_number: int | None
    discipline: str | None
    document_code: str | None
    ntd_refs: list[str]


@dataclass
class _DocAccumulator:
    document_id: str
    filename: str
    job_status: str
    tokens_count: int = 0
    tokens_sampled: int = 0
    rows: list[_TokenRow] = field(default_factory=list)


def build_bundle_project_context(
    settings: Settings,
    batch_id: str,
    *,
    max_tokens_per_document: int = 120,
    max_excerpts: int = 48,
    use_search: bool = True,
    persist: bool = True,
) -> BundleProjectContextResponse:
    """Собирает контекст комплекта из RAG (токены + опционально hybrid search)."""
    opts = _BuildOptions(
        max_tokens_per_document=max_tokens_per_document,
        max_excerpts=max_excerpts,
        use_search=use_search,
    )
    detail = get_bundle_detail(settings, batch_id)
    if detail is None:
        raise ValueError("Комплект не найден.")

    meta = read_bundle_meta(settings, batch_id) or {}
    rag_project_id = (detail.rag_ingest.project_id if detail.rag_ingest else None) or None

    indexed_files = [f for f in detail.pipeline_files if f.job_status == "indexed" and f.document_id]
    missing_files = [f for f in detail.pipeline_files if f.job_status == "missing"]
    if missing_files and not indexed_files:
        raise ValueError(RAG_DOCUMENT_MISSING_MSG)
    if not indexed_files and detail.pipeline_status != "indexed":
        raise ValueError(
            "Комплект ещё не проиндексирован в RAG. Дождитесь статуса «Индексация завершена» "
            "или перезапустите отправку в RAG."
        )

    if not settings.rag_enabled:
        raise ValueError("RAG отключён (RAG_ENABLED=false).")

    if not rag_project_id:
        rag_raw = meta.get("rag_ingest") or {}
        rag_project_id = rag_raw.get("project_id")

    if not rag_project_id:
        raise ValueError("Не найден project_id RAG для комплекта.")

    base = settings.rag_api_url.rstrip("/")
    docs: dict[str, _DocAccumulator] = {}
    for file_row in detail.pipeline_files:
        if not file_row.document_id:
            continue
        docs[file_row.document_id] = _DocAccumulator(
            document_id=file_row.document_id,
            filename=file_row.filename,
            job_status=file_row.job_status,
            tokens_count=file_row.tokens_count,
        )

    try:
        with httpx.Client(timeout=settings.rag_http_timeout_seconds, trust_env=False) as client:
            for doc_id, acc in docs.items():
                if acc.job_status != "indexed":
                    continue
                acc.rows = _fetch_document_tokens(
                    client,
                    base,
                    doc_id,
                    limit=opts.max_tokens_per_document,
                )
                acc.tokens_sampled = len(acc.rows)
                if acc.tokens_count <= 0 and acc.tokens_sampled:
                    acc.tokens_count = acc.tokens_sampled

            search_excerpts: list[BundleContextExcerpt] = []
            if opts.use_search and indexed_files:
                search_excerpts = _fetch_search_excerpts(
                    client,
                    base,
                    rag_project_id,
                    top_k=opts.search_top_k,
                )
    except httpx.HTTPError as exc:
        logger.error("RAG context build failed batch=%s: %s", batch_id, exc)
        raise ValueError(f"RAG Platform недоступна ({base}): {exc}") from exc

    if indexed_files and not any(acc.rows for acc in docs.values()):
        raise ValueError(RAG_DOCUMENT_MISSING_MSG)

    excerpts = _merge_excerpts(docs, search_excerpts, max_excerpts=opts.max_excerpts)
    structured = _build_structured(
        batch_id=batch_id,
        project_cipher=detail.project_cipher,
        rag_project_id=rag_project_id,
        pipeline_status=detail.pipeline_status,
        pipeline_label=detail.pipeline_label,
        docs=docs,
        excerpts=excerpts,
        documents_total=len(detail.pipeline_files) or detail.total_files,
    )
    summary = _build_summary(structured, excerpts)
    ai_context_json = _build_ai_context_json(structured, summary, excerpts)

    status: str = "ready"
    message = ""
    if structured.documents_indexed < structured.documents_total:
        status = "partial"
        message = (
            f"Контекст собран по {structured.documents_indexed} из {structured.documents_total} "
            "документов с завершённой индексацией."
        )
    elif not excerpts:
        status = "partial"
        message = "Индексация завершена, но текстовые фрагменты не извлечены."

    built_at = datetime.now(timezone.utc)
    response = BundleProjectContextResponse(
        batch_id=batch_id,
        status=status,  # type: ignore[arg-type]
        built_at=built_at,
        summary=summary,
        structured=structured,
        excerpts=excerpts,
        ai_context_json=ai_context_json,
        message=message,
    )

    if persist:
        meta["project_context"] = {
            "status": status,
            "built_at": built_at.isoformat(),
            "summary": summary,
            "structured": structured.model_dump(mode="json"),
            "excerpts": [e.model_dump(mode="json") for e in excerpts],
            "ai_context_json": ai_context_json,
            "message": message,
        }
        write_bundle_meta(settings, batch_id, meta)

    return response


def get_stored_bundle_project_context(
    settings: Settings,
    batch_id: str,
) -> BundleProjectContextResponse | None:
    meta = read_bundle_meta(settings, batch_id)
    if not meta:
        return None
    raw = meta.get("project_context")
    if not isinstance(raw, dict):
        return None
    try:
        structured = BundleContextStructured.model_validate(raw.get("structured") or {})
        excerpts = [
            BundleContextExcerpt.model_validate(row)
            for row in (raw.get("excerpts") or [])
            if isinstance(row, dict)
        ]
        built_at = raw.get("built_at")
        if isinstance(built_at, str):
            built = datetime.fromisoformat(built_at.replace("Z", "+00:00"))
        else:
            built = datetime.now(timezone.utc)
        return BundleProjectContextResponse(
            batch_id=batch_id,
            status=raw.get("status", "ready"),  # type: ignore[arg-type]
            built_at=built,
            summary=str(raw.get("summary") or ""),
            structured=structured,
            excerpts=excerpts,
            ai_context_json=str(raw.get("ai_context_json") or ""),
            message=str(raw.get("message") or ""),
        )
    except Exception as exc:
        logger.warning("Invalid stored project_context batch=%s: %s", batch_id, exc)
        return None


def _fetch_document_tokens(
    client: httpx.Client,
    base: str,
    document_id: str,
    *,
    limit: int,
) -> list[_TokenRow]:
    try:
        response = client.get(
            f"{base}/documents/{document_id}/tokens",
            params={"limit": limit, "offset": 0},
        )
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 404:
            logger.warning("RAG document not found for tokens: %s", document_id)
            return []
        raise
    payload = response.json()
    items = payload.get("items") or []
    rows: list[_TokenRow] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        text = str(item.get("text") or "").strip()
        if len(text) < 12:
            continue
        rows.append(
            _TokenRow(
                text=text,
                element_type=str(item.get("element_type") or "text"),
                page_number=item.get("page_number"),
                discipline=item.get("discipline"),
                document_code=item.get("document_code"),
                ntd_refs=[str(x) for x in (item.get("ntd_refs") or []) if x],
            )
        )
    rows.sort(key=lambda r: (_ELEMENT_PRIORITY.get(r.element_type, 99), len(r.text)))
    return rows


def _fetch_search_excerpts(
    client: httpx.Client,
    base: str,
    project_id: str,
    *,
    top_k: int,
) -> list[BundleContextExcerpt]:
    seen: set[str] = set()
    excerpts: list[BundleContextExcerpt] = []
    for query in _SEED_SEARCH_QUERIES:
        response = client.post(
            f"{base}/search/project-analysis",
            json={
                "project_id": project_id,
                "query": query,
                "filters": {},
                "top_k": top_k,
                "debug": False,
            },
        )
        response.raise_for_status()
        for hit in response.json().get("hits") or []:
            if not isinstance(hit, dict):
                continue
            text = str(hit.get("text") or "").strip()
            if len(text) < 20:
                continue
            key = text[:240]
            if key in seen:
                continue
            seen.add(key)
            excerpts.append(
                BundleContextExcerpt(
                    text=text[:1200],
                    source="search",
                    document_id=str(hit.get("document_id")) if hit.get("document_id") else None,
                    filename=hit.get("document_name"),
                    page_number=hit.get("page_number"),
                    element_type=hit.get("element_type"),
                    discipline=(hit.get("metadata") or {}).get("discipline")
                    if isinstance(hit.get("metadata"), dict)
                    else None,
                    document_code=hit.get("document_code"),
                    score=float(hit.get("score") or 0),
                )
            )
    excerpts.sort(key=lambda e: -(e.score or 0))
    return excerpts


def _merge_excerpts(
    docs: dict[str, _DocAccumulator],
    search_excerpts: list[BundleContextExcerpt],
    *,
    max_excerpts: int,
) -> list[BundleContextExcerpt]:
    token_excerpts: list[BundleContextExcerpt] = []
    for acc in docs.values():
        for row in acc.rows:
            token_excerpts.append(
                BundleContextExcerpt(
                    text=row.text[:1200],
                    source="token",
                    document_id=acc.document_id,
                    filename=acc.filename,
                    page_number=row.page_number,
                    element_type=row.element_type,
                    discipline=row.discipline,
                    document_code=row.document_code,
                )
            )
    token_excerpts.sort(
        key=lambda e: (
            _ELEMENT_PRIORITY.get(e.element_type or "text", 99),
            -len(e.text),
        )
    )

    merged: list[BundleContextExcerpt] = []
    seen: set[str] = set()
    for excerpt in token_excerpts + search_excerpts:
        key = excerpt.text[:200]
        if key in seen:
            continue
        seen.add(key)
        merged.append(excerpt)
        if len(merged) >= max_excerpts:
            break
    return merged


def _build_structured(
    *,
    batch_id: str,
    project_cipher: str | None,
    rag_project_id: str,
    pipeline_status: str,
    pipeline_label: str,
    docs: dict[str, _DocAccumulator],
    excerpts: list[BundleContextExcerpt],
    documents_total: int,
) -> BundleContextStructured:
    element_types: Counter[str] = Counter()
    disciplines: set[str] = set()
    document_codes: set[str] = set()
    ntd_refs: set[str] = set()
    doc_summaries: list[BundleContextDocumentSummary] = []
    total_tokens = 0
    indexed_count = 0

    for acc in docs.values():
        if acc.job_status == "indexed":
            indexed_count += 1
        total_tokens += acc.tokens_count
        doc_disciplines: set[str] = set()
        doc_codes: set[str] = set()
        for row in acc.rows:
            element_types[row.element_type] += 1
            if row.discipline:
                disciplines.add(row.discipline)
                doc_disciplines.add(row.discipline)
            if row.document_code:
                document_codes.add(row.document_code)
                doc_codes.add(row.document_code)
            for ref in row.ntd_refs:
                ntd_refs.add(ref)
        doc_summaries.append(
            BundleContextDocumentSummary(
                document_id=acc.document_id,
                filename=acc.filename,
                job_status=acc.job_status,
                tokens_count=acc.tokens_count,
                tokens_sampled=acc.tokens_sampled,
                disciplines=sorted(doc_disciplines),
                document_codes=sorted(doc_codes),
            )
        )

    for excerpt in excerpts:
        if excerpt.discipline:
            disciplines.add(excerpt.discipline)
        if excerpt.document_code:
            document_codes.add(excerpt.document_code)
        if excerpt.element_type:
            element_types[excerpt.element_type] += 1

    doc_summaries.sort(key=lambda d: d.filename)
    return BundleContextStructured(
        batch_id=batch_id,
        project_cipher=project_cipher,
        rag_project_id=rag_project_id,
        collection_label=COLLECTION_LABEL,
        pipeline_status=pipeline_status,
        pipeline_label=pipeline_label,
        documents_indexed=indexed_count,
        documents_total=documents_total,
        total_tokens=total_tokens,
        disciplines=sorted(disciplines),
        document_codes=sorted(document_codes),
        element_types=dict(element_types.most_common()),
        documents=doc_summaries,
        ntd_refs=sorted(ntd_refs)[:40],
    )


def _build_summary(structured: BundleContextStructured, excerpts: list[BundleContextExcerpt]) -> str:
    parts = [
        f"Комплект {structured.batch_id}"
        + (f" (шифр {structured.project_cipher})" if structured.project_cipher else "")
        + f": {structured.documents_indexed} документ(ов) в RAG, "
        f"{structured.total_tokens} инженерных токенов.",
    ]
    if structured.disciplines:
        parts.append(f"Разделы/дисциплины: {', '.join(structured.disciplines[:12])}.")
    if structured.document_codes:
        parts.append(f"Шифры документов: {', '.join(structured.document_codes[:12])}.")
    if structured.ntd_refs:
        parts.append(f"Упоминания НТД: {', '.join(structured.ntd_refs[:8])}.")
    if excerpts:
        lead = excerpts[0].text.replace("\n", " ").strip()
        if len(lead) > 320:
            lead = lead[:319] + "…"
        parts.append(f"Ключевой фрагмент: {lead}")
    return " ".join(parts)


def _build_ai_context_json(
    structured: BundleContextStructured,
    summary: str,
    excerpts: list[BundleContextExcerpt],
) -> str:
    payload: dict[str, Any] = {
        "purpose": (
            "Проектный контекст, автоматически собранный из проиндексированного комплекта PDF "
            "(раздел «Анализ проекта»): метаданные, агрегаты и выдержки из инженерных токенов RAG."
        ),
        "summary": summary,
        "structured": structured.model_dump(mode="json"),
        "excerpts": [e.model_dump(mode="json") for e in excerpts[:32]],
        "model_instructions": (
            "Используй summary и excerpts как фактический контекст по загруженной документации. "
            "При противоречиях указывай источник (filename, page_number). "
            "Не выдумывай шифры, нормы и объёмы, которых нет в excerpts."
        ),
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)
