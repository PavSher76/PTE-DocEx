"""Финализация пакета после обработки всех документов."""

from __future__ import annotations

import logging
from datetime import datetime

from sqlalchemy.orm import Session

from app.config import Settings
from app.ism.ai_pipeline import run_batch_ai_pipeline
from app.ism.interface_graph import build_interfaces_for_batch
from app.ism.models import IsmDocument, IsmProcessingJob, IsmUploadBatch
from app.ism.qdrant_sync import index_batch_interfaces
from app.ism.reports import build_batch_report

logger = logging.getLogger(__name__)

_TERMINAL = frozenset({"indexed", "failed", "needs_review", "cancelled"})


def maybe_finalize_batch(db: Session, settings: Settings, batch_id: str) -> None:
    jobs = list(db.query(IsmProcessingJob).filter(IsmProcessingJob.batch_id == batch_id).all())
    if not jobs or not all(j.status in _TERMINAL for j in jobs):
        return

    batch = db.get(IsmUploadBatch, batch_id)
    if not batch or batch.status == "completed":
        return

    documents = list(db.query(IsmDocument).filter(IsmDocument.batch_id == batch_id).all())
    try:
        build_interfaces_for_batch(db, batch_id, documents)
        if settings.rag_enabled:
            index_batch_interfaces(settings, db, batch_id)
        run_batch_ai_pipeline(db, settings, batch_id)
        build_batch_report(db, batch_id)
        batch.status = "completed"
        batch.reviewed_at = batch.reviewed_at or datetime.utcnow()
        db.commit()
        logger.info("ISM batch %s finalized (%s docs)", batch_id, len(documents))
    except Exception as exc:
        logger.exception("ISM batch finalize failed %s: %s", batch_id, exc)
        batch.status = "completed_with_errors"
        db.commit()
