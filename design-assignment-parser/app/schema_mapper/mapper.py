"""Применение corrections.yaml и нормализаторов к canonical."""

from __future__ import annotations

import re
from datetime import date
from pathlib import Path
from typing import Any
from uuid import uuid4

import yaml

from app.models.canonical import DesignAssignmentCanonical, TraceabilityEntry


def apply_corrections(
    canonical: DesignAssignmentCanonical, corrections_path: Path | None
) -> DesignAssignmentCanonical:
    if not corrections_path or not corrections_path.exists():
        return canonical
    data = yaml.safe_load(corrections_path.read_text(encoding="utf-8")) or {}
    for item in data.get("overrides", []):
        path = item.get("canonical_path")
        value = item.get("value")
        if not path:
            continue
        _set_by_path(canonical, path, value)
        canonical.traceability.append(
            TraceabilityEntry(
                canonical_path=path,
                corrected=True,
                corrected_value=value,
                corrected_by=item.get("corrected_by", "manual"),
                correction_reason=item.get("reason", ""),
                confidence=1.0,
                extraction_method="manual_correction",
            )
        )
    return canonical


def normalize_canonical(canonical: DesignAssignmentCanonical, mapping: dict) -> DesignAssignmentCanonical:
    canonical.ensure_document_id()
    if not canonical.document.document_type_code:
        canonical.document.document_type_code = "05.03"
    if not canonical.document.schema_version:
        canonical.document.schema_version = "01.00"
    if not canonical.document.version_number:
        canonical.document.version_number = 1

    for path, spec in mapping.items():
        val = _get_by_path(canonical, path)
        if val is None:
            default = spec.get("default_value")
            if default is not None:
                _set_by_path(canonical, path, default)
            continue
        norm_name = spec.get("normalizer")
        if norm_name:
            _set_by_path(canonical, path, _run_normalizer(norm_name, val))
    return canonical


def _run_normalizer(name: str, value: Any) -> Any:
    if name == "iso_date" and isinstance(value, date):
        return value.isoformat()
    if name == "guid":
        s = str(value).strip()
        return s if s else str(uuid4())
    return value


def _get_by_path(obj: Any, path: str) -> Any:
    parts = path.split(".")
    cur: Any = obj
    for part in parts:
        if cur is None:
            return None
        if hasattr(cur, part):
            cur = getattr(cur, part)
        elif isinstance(cur, dict):
            cur = cur.get(part)
        else:
            return None
    return cur


def _set_by_path(obj: Any, path: str, value: Any) -> None:
    parts = path.split(".")
    cur = obj
    for part in parts[:-1]:
        cur = getattr(cur, part)
    setattr(cur, parts[-1], value)


def coverage_mandatory_fields(canonical: DesignAssignmentCanonical, mapping: dict) -> tuple[int, int, list[str]]:
    required_paths = [p for p, s in mapping.items() if s.get("required")]
    missing: list[str] = []
    filled = 0
    for path in required_paths:
        val = _get_by_path(canonical, path)
        if val is None or (isinstance(val, str) and not val.strip()):
            missing.append(path)
        else:
            filled += 1
    return filled, len(required_paths), missing
