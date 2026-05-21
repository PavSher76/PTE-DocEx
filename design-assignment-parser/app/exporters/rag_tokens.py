"""RAG engineering tokens с traceability."""

from __future__ import annotations

import json
from pathlib import Path
from uuid import uuid4

from app.models.canonical import DesignAssignmentCanonical


def export_rag_tokens(canonical: DesignAssignmentCanonical, path: Path) -> Path:
    doc_id = canonical.document.document_id or str(uuid4())
    tokens: list[dict] = []

    def add(
        token_type: str,
        text: str,
        *,
        page: int | None = None,
        bbox: list[float] | None = None,
        canonical_path: str,
        xml_path: str | None = None,
        confidence: float = 0.0,
    ) -> None:
        if not text or not str(text).strip():
            return
        tokens.append(
            {
                "token_id": str(uuid4()),
                "document_id": doc_id,
                "token_type": token_type,
                "page_number": page,
                "bbox": bbox,
                "canonical_path": canonical_path,
                "xml_path": xml_path,
                "text": str(text).strip(),
                "confidence": confidence,
            }
        )

    d = canonical.document
    add("document_metadata", f"Документ {d.document_number or 'б/н'} от {d.document_date}", canonical_path="document")
    if canonical.object.name:
        add("object_metadata", canonical.object.name, canonical_path="object.name", xml_path="/Document/Content/ConstructionObjects/ConstructionObject/Name")
    if canonical.participants.author.full_name:
        add("participant", canonical.participants.author.full_name, canonical_path="participants.author.full_name")

    for i, req in enumerate(canonical.requirements):
        add(
            "design_requirement",
            req.text,
            page=req.source_page,
            bbox=req.bbox,
            canonical_path=req.canonical_path or f"requirements[{i}]",
            xml_path=req.xml_path,
            confidence=req.confidence,
        )

    for src in canonical.design_requirements.source_data:
        add("source_data", src, canonical_path="design_requirements.source_data")

    path.write_text(json.dumps(tokens, ensure_ascii=False, indent=2), encoding="utf-8")
    return path
