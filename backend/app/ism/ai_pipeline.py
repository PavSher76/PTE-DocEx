"""AI batch pipeline: классификация, дубликаты, конфликты (Ollama)."""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Any

from rapidfuzz import fuzz
from sqlalchemy.orm import Session

from app.config import Settings
from app.ism.models import IsmDocument, IsmInterface, IsmUploadBatch
from app.services.ollama import OllamaClient

logger = logging.getLogger(__name__)

ISM_BATCH_AI_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": ["classifications", "duplicates", "conflicts"],
    "properties": {
        "classifications": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["document_id", "suggested_type", "confidence", "reason"],
                "properties": {
                    "document_id": {"type": "string"},
                    "suggested_type": {"type": "string"},
                    "confidence": {"type": "number"},
                    "reason": {"type": "string"},
                },
            },
        },
        "duplicates": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["document_a", "document_b", "similarity", "reason"],
                "properties": {
                    "document_a": {"type": "string"},
                    "document_b": {"type": "string"},
                    "similarity": {"type": "number"},
                    "reason": {"type": "string"},
                },
            },
        },
        "conflicts": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["document_a", "document_b", "severity", "reason"],
                "properties": {
                    "document_a": {"type": "string"},
                    "document_b": {"type": "string"},
                    "severity": {"type": "string", "enum": ["info", "warning", "critical"]},
                    "reason": {"type": "string"},
                },
            },
        },
    },
}


def _heuristic_duplicates(documents: list[IsmDocument]) -> list[dict[str, Any]]:
    pairs: list[dict[str, Any]] = []
    for i, a in enumerate(documents):
        for b in documents[i + 1 :]:
            score = fuzz.token_sort_ratio(
                f"{a.code} {a.title}".strip(),
                f"{b.code} {b.title}".strip(),
            )
            if score >= 88 or (a.code and a.code == b.code):
                pairs.append(
                    {
                        "document_a": a.id,
                        "document_b": b.id,
                        "similarity": score / 100.0,
                        "reason": "Схожие код/название (эвристика)",
                        "source": "heuristic",
                    }
                )
    return pairs


def _build_prompt(documents: list[IsmDocument], interfaces: list[IsmInterface]) -> str:
    docs_payload = [
        {
            "document_id": d.id,
            "code": d.code,
            "title": d.title,
            "document_type": d.document_type,
            "summary": (d.ai_summary or "")[:1500],
        }
        for d in documents
    ]
    iface_payload = [
        {
            "source": i.source_document_id,
            "target": i.target_document_id,
            "link_type": i.link_type,
            "text": (i.reference_text or "")[:300],
        }
        for i in interfaces[:80]
    ]
    return json.dumps(
        {
            "task": (
                "Проанализируй пакет документов ИСМ (интегрированная система менеджмента). "
                "Классифицируй тип каждого документа (SOP, FORM, CHECKLIST, REGISTER, INSTRUCTION, "
                "REQUIREMENT, PROCESS_MAP, TEMPLATE, OTHER). Найди вероятные дубликаты и логические конфликты."
            ),
            "documents": docs_payload,
            "interfaces": iface_payload,
            "response_schema": ISM_BATCH_AI_SCHEMA,
        },
        ensure_ascii=False,
    )


async def _run_ollama(settings: Settings, prompt: str) -> dict[str, Any] | None:
    client = OllamaClient(settings)
    data = await client._generate_json(prompt, schema=ISM_BATCH_AI_SCHEMA)
    return data if isinstance(data, dict) else None


def run_batch_ai_pipeline(db: Session, settings: Settings, batch_id: str) -> dict[str, Any]:
    batch = db.get(IsmUploadBatch, batch_id)
    if not batch:
        return {"error": "batch_not_found"}

    documents = list(db.query(IsmDocument).filter(IsmDocument.batch_id == batch_id).all())
    if not documents:
        batch.ai_pipeline_status = "skipped"
        db.commit()
        return {"status": "skipped", "reason": "no_documents"}

    batch.ai_pipeline_status = "running"
    db.commit()

    interfaces = list(db.query(IsmInterface).filter(IsmInterface.batch_id == batch_id).all())
    heuristic_dupes = _heuristic_duplicates(documents)

    ai_result: dict[str, Any] = {
        "classifications": [],
        "duplicates": heuristic_dupes,
        "conflicts": [],
        "ollama_used": False,
    }

    if settings.ollama_base_url:
        try:
            prompt = _build_prompt(documents, interfaces)
            ollama_data = asyncio.run(_run_ollama(settings, prompt))
            if ollama_data:
                ai_result["ollama_used"] = True
                ai_result["classifications"] = ollama_data.get("classifications") or []
                for dup in ollama_data.get("duplicates") or []:
                    if isinstance(dup, dict):
                        dup.setdefault("source", "ollama")
                        ai_result["duplicates"].append(dup)
                ai_result["conflicts"] = ollama_data.get("conflicts") or []
        except Exception as exc:
            logger.exception("ISM AI pipeline failed batch=%s: %s", batch_id, exc)
            ai_result["error"] = str(exc)

    for item in ai_result.get("classifications") or []:
        if not isinstance(item, dict):
            continue
        doc_id = item.get("document_id")
        doc = next((d for d in documents if d.id == doc_id), None)
        if doc:
            doc.ai_classification = item
            suggested = item.get("suggested_type")
            if suggested and doc.document_type == "OTHER":
                doc.document_type = str(suggested)[:64]

    for dup in ai_result.get("duplicates") or []:
        if not isinstance(dup, dict):
            continue
        a, b = dup.get("document_a"), dup.get("document_b")
        if a and b:
            db.add(
                IsmInterface(
                    batch_id=batch_id,
                    source_document_id=a,
                    target_document_id=b,
                    link_type="duplicates",
                    reference_text=dup.get("reason", "AI: возможный дубликат"),
                    confidence=float(dup.get("similarity", 0.7)),
                    extra={"source": dup.get("source", "ai")},
                )
            )

    for conf in ai_result.get("conflicts") or []:
        if not isinstance(conf, dict):
            continue
        a, b = conf.get("document_a"), conf.get("document_b")
        if a and b:
            db.add(
                IsmInterface(
                    batch_id=batch_id,
                    source_document_id=a,
                    target_document_id=b,
                    link_type="conflicts",
                    reference_text=conf.get("reason", "AI: конфликт"),
                    confidence=0.6 if conf.get("severity") == "warning" else 0.85,
                    extra={"severity": conf.get("severity", "warning")},
                )
            )

    batch.ai_pipeline_json = ai_result
    batch.ai_pipeline_status = "done" if ai_result.get("ollama_used") or heuristic_dupes else "partial"
    db.commit()
    return ai_result
