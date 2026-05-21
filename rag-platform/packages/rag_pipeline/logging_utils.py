"""Контекстные логи конвейера: job → этап → метрики."""

from __future__ import annotations

import logging
import time
from contextlib import contextmanager
from typing import Any, Iterator
from uuid import UUID

LOG = logging.getLogger("rag.pipeline")


def configure_pipeline_logging(level: int = logging.INFO) -> None:
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
        datefmt="%H:%M:%S",
        force=True,
    )
    logging.getLogger("rag.pipeline").setLevel(level)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)


def _fmt(ctx: dict[str, Any]) -> str:
    if not ctx:
        return ""
    parts = [f"{k}={v}" for k, v in ctx.items() if v is not None]
    return " | " + " | ".join(parts) if parts else ""


@contextmanager
def pipeline_step(
    job_id: UUID | str,
    step: str,
    *,
    project_id: str | None = None,
    document_id: UUID | str | None = None,
    filename: str | None = None,
    collection: str | None = None,
    extra: dict[str, Any] | None = None,
) -> Iterator[None]:
    ctx: dict[str, Any] = {
        "project": project_id,
        "doc": str(document_id)[:8] if document_id else None,
        "file": filename,
        "collection": collection,
        **(extra or {}),
    }
    t0 = time.perf_counter()
    LOG.info("▶ job=%s | %s%s", job_id, step, _fmt(ctx))
    try:
        yield
    except Exception as exc:
        LOG.exception(
            "✗ job=%s | %s | error=%s%s",
            job_id,
            step,
            exc,
            _fmt(ctx),
        )
        raise
    else:
        LOG.info("✓ job=%s | %s | %.2fs%s", job_id, step, time.perf_counter() - t0, _fmt(ctx))
