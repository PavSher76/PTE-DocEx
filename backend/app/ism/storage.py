"""Файловое хранилище документов ИСМ."""

from __future__ import annotations

from pathlib import Path

from app.config import Settings


def ism_storage_root(settings: Settings) -> Path:
    root = settings.storage_dir / "ism_documents"
    root.mkdir(parents=True, exist_ok=True)
    return root


def document_file_path(settings: Settings, document_id: str, filename: str) -> Path:
    doc_dir = ism_storage_root(settings) / document_id
    doc_dir.mkdir(parents=True, exist_ok=True)
    return doc_dir / Path(filename).name
