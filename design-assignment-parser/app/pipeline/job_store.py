from __future__ import annotations

from threading import Lock
from uuid import UUID

from app.models.pipeline_state import PipelineJob

_lock = Lock()
_jobs: dict[UUID, PipelineJob] = {}


def save_job(job: PipelineJob) -> None:
    with _lock:
        _jobs[job.job_id] = job


def get_job(job_id: UUID) -> PipelineJob | None:
    with _lock:
        return _jobs.get(job_id)
