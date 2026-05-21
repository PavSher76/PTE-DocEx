from __future__ import annotations

import json
from pathlib import Path

from app.models.canonical import DesignAssignmentCanonical


def export_canonical_json(canonical: DesignAssignmentCanonical, path: Path) -> Path:
    path.write_text(
        json.dumps(canonical.model_dump(mode="json"), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return path


def export_requirements_json(canonical: DesignAssignmentCanonical, path: Path) -> Path:
    payload = [r.model_dump(mode="json") for r in canonical.requirements]
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def export_traceability_json(canonical: DesignAssignmentCanonical, path: Path) -> Path:
    payload = [t.model_dump(mode="json") for t in canonical.traceability]
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def export_normalized_for_rag(canonical: DesignAssignmentCanonical, path: Path) -> Path:
    """Уплощённый JSON для токенизации."""
    chunks = {
        "document": canonical.document.model_dump(mode="json"),
        "object": canonical.object.model_dump(mode="json"),
        "participants": canonical.participants.model_dump(mode="json"),
        "design_requirements": canonical.design_requirements.model_dump(mode="json"),
    }
    path.write_text(json.dumps(chunks, ensure_ascii=False, indent=2), encoding="utf-8")
    return path
