"""Реестр версий XSD Минстроя."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

from app.config import SCHEMAS_ROOT, Settings


@dataclass(frozen=True)
class SchemaVersionInfo:
    key: str
    schema_version: str
    type_code: str
    schema_path: Path
    mapping_path: Path
    meta_path: Path
    schema_url: str
    effective_from: str
    published_at: str


def list_schema_versions() -> list[str]:
    if not SCHEMAS_ROOT.is_dir():
        return []
    return sorted(p.name for p in SCHEMAS_ROOT.iterdir() if p.is_dir() and (p / "schema.xsd").exists())


def load_schema_version(settings: Settings) -> SchemaVersionInfo:
    key = settings.active_minstroy_design_assignment_schema_version
    base = SCHEMAS_ROOT / key
    meta_file = base / "meta.yaml"
    if not meta_file.exists():
        raise FileNotFoundError(f"Схема {key} не найдена в {base}")
    meta = yaml.safe_load(meta_file.read_text(encoding="utf-8")) or {}
    return SchemaVersionInfo(
        key=key,
        schema_version=str(meta.get("schema_version", "01.00")),
        type_code=str(meta.get("type_code", "05.03")),
        schema_path=base / str(meta.get("schema_file", "schema.xsd")),
        mapping_path=base / str(meta.get("mapping_file", "mapping.yaml")),
        meta_path=meta_file,
        schema_url=str(meta.get("schema_url", "")),
        effective_from=str(meta.get("effective_from", "")),
        published_at=str(meta.get("published_at", "")),
    )


def load_mapping(settings: Settings) -> dict:
    info = load_schema_version(settings)
    return yaml.safe_load(info.mapping_path.read_text(encoding="utf-8")) or {}
