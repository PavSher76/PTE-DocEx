"""Пакетная загрузка документов ИСМ."""

from __future__ import annotations

import io
import zipfile
from datetime import datetime
from pathlib import Path
from typing import BinaryIO

from sqlalchemy.orm import Session

from app.config import Settings
from app.ism.constants import ISM_ALLOWED_SUFFIXES
from app.ism.models import (
    IsmDocument,
    IsmDocumentFile,
    IsmDocumentVersion,
    IsmProcessingJob,
    IsmUploadBatch,
)
from app.ism.processor import process_document_job
from app.ism.storage import document_file_path
from app.services.ism_extract import is_ism_allowed_filename


def _safe_name(name: str) -> str:
    return Path(name).name.replace("..", "_")


def create_batch_upload(
    db: Session,
    settings: Settings,
    *,
    files: list[tuple[str, bytes]],
    ism_process_id: str | None,
    document_type: str = "OTHER",
    owner: str = "ИСМ",
    status: str = "active",
    revision: str = "A",
    discipline: str | None = None,
    comment: str = "",
    title: str = "",
    project_cipher: str | None = None,
) -> tuple[IsmUploadBatch, list[IsmProcessingJob]]:
    batch = IsmUploadBatch(
        title=title or f"Пакет ИСМ {datetime.utcnow():%Y-%m-%d %H:%M}",
        project_cipher=project_cipher,
        comment=comment,
        status="processing",
    )
    db.add(batch)
    db.flush()

    jobs: list[IsmProcessingJob] = []
    for rel_name, data in files:
        filename = _safe_name(rel_name)
        if not is_ism_allowed_filename(filename):
            continue
        doc = IsmDocument(
            ism_process_id=ism_process_id,
            batch_id=batch.id,
            document_type=document_type,
            title=Path(filename).stem,
            code="",
            revision=revision,
            status=status,
            owner=owner,
            discipline=discipline,
        )
        db.add(doc)
        db.flush()

        version = IsmDocumentVersion(document_id=doc.id, revision=revision)
        db.add(version)
        db.flush()

        dest = document_file_path(settings, doc.id, filename)
        dest.write_bytes(data)

        db.add(
            IsmDocumentFile(
                document_id=doc.id,
                version_id=version.id,
                filename=filename,
                relative_path=rel_name,
                file_type=Path(filename).suffix.lower().lstrip("."),
                size_bytes=len(data),
                storage_path=str(dest),
            )
        )

        job = IsmProcessingJob(
            document_id=doc.id,
            batch_id=batch.id,
            status="queued",
            progress=0,
            stage="queued",
        )
        db.add(job)
        jobs.append(job)

    db.commit()
    db.refresh(batch)
    return batch, jobs


def extract_zip_entries(data: bytes) -> list[tuple[str, bytes]]:
    entries: list[tuple[str, bytes]] = []
    with zipfile.ZipFile(io.BytesIO(data)) as zf:
        for info in zf.infolist():
            if info.is_dir():
                continue
            name = _safe_name(info.filename)
            if not is_ism_allowed_filename(name):
                continue
            entries.append((name, zf.read(info)))
    return entries


def enqueue_batch_processing(batch_id: str, jobs: list[IsmProcessingJob], background_tasks) -> None:
    for job in jobs:
        background_tasks.add_task(process_document_job, job.document_id, job.id)
