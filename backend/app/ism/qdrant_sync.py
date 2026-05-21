"""Синхронизация токенов ИСМ в Qdrant через RAG Platform API."""

from __future__ import annotations

import logging
import uuid
from typing import Literal

import httpx
from sqlalchemy.orm import Session

from app.config import Settings
from app.ism.models import IsmDocument, IsmInterface, IsmRagToken, IsmRequirement
from app.services.ism_rag import resolve_rag_project_id

logger = logging.getLogger(__name__)

IsmColl = Literal["documents", "requirements", "interfaces"]


def index_document_vectors(
    settings: Settings,
    db: Session,
    document: IsmDocument,
    *,
    tokens: list[IsmRagToken],
    requirements: list[IsmRequirement] | None = None,
) -> dict[str, int]:
    if not settings.rag_enabled:
        return {}
    project_id = resolve_rag_project_id(None, document.batch_id or document.id)
    if not project_id.startswith("ISM-"):
        project_id = f"ISM-{project_id}"

    items: list[dict] = []
    for t in tokens:
        coll: IsmColl = "requirements" if t.token_type == "requirement" else "documents"
        items.append(
            {
                "point_id": t.id,
                "collection": coll,
                "text": t.text,
                "payload": {
                    "token_type": t.token_type,
                    "document_code": t.document_code,
                    "document_type": t.document_type,
                    "revision": t.revision,
                    "section": t.section,
                    "process_id": t.process_id,
                    "source_page": t.source_page,
                    "bbox": t.bbox,
                },
            }
        )
    for req in requirements or []:
        items.append(
            {
                "point_id": str(uuid.uuid4()),
                "collection": "requirements",
                "text": req.text,
                "payload": {
                    "requirement_id": req.id,
                    "section": req.section,
                    "document_code": document.code,
                },
            }
        )

    base = settings.rag_api_url.rstrip("/")
    try:
        with httpx.Client(timeout=settings.rag_http_timeout_seconds, trust_env=False) as client:
            response = client.post(
                f"{base}/ism/vectors/index",
                json={
                    "project_id": project_id,
                    "document_id": document.id,
                    "items": items,
                    "delete_document_first": True,
                },
            )
            response.raise_for_status()
            data = response.json()
            for t in tokens:
                t.qdrant_point_id = t.id
            db.commit()
            return data.get("collections") or {}
    except httpx.HTTPError as exc:
        logger.error("ISM Qdrant index failed doc=%s: %s", document.id, exc)
        raise


def index_batch_interfaces(settings: Settings, db: Session, batch_id: str) -> int:
    if not settings.rag_enabled:
        return 0
    interfaces = list(db.query(IsmInterface).filter(IsmInterface.batch_id == batch_id).all())
    if not interfaces:
        return 0
    project_id = f"ISM-{batch_id[:12]}"
    items = []
    for iface in interfaces:
        text = (
            f"{iface.link_type}: {iface.reference_text} "
            f"→ {iface.target_document_code or iface.target_discipline or '?'}"
        )
        items.append(
            {
                "point_id": str(uuid.uuid4()),
                "collection": "interfaces",
                "text": text[:2000],
                "payload": {
                    "interface_id": iface.id,
                    "link_type": iface.link_type,
                    "source_document_id": iface.source_document_id,
                    "target_document_id": iface.target_document_id,
                    "confidence": iface.confidence,
                },
            }
        )
    base = settings.rag_api_url.rstrip("/")
    with httpx.Client(timeout=settings.rag_http_timeout_seconds, trust_env=False) as client:
        response = client.post(
            f"{base}/ism/vectors/index",
            json={
                "project_id": project_id,
                "document_id": f"batch-{batch_id}",
                "items": items,
                "delete_document_first": False,
            },
        )
        response.raise_for_status()
    return len(items)
