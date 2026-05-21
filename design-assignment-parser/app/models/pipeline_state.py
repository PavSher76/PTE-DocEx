from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from app.models.canonical import DesignAssignmentCanonical
from app.models.layout import PageAnalysis


class JobStatus(str, Enum):
    queued = "queued"
    running = "running"
    completed = "completed"
    failed = "failed"


class QualityGateResult(BaseModel):
    gate_id: str
    name: str
    passed: bool
    detail: str = ""


class PipelineJob(BaseModel):
    job_id: UUID = Field(default_factory=uuid4)
    status: JobStatus = JobStatus.queued
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    schema_version_key: str = "v01_00"
    source_pdf: Path | None = None
    work_dir: Path | None = None
    pdf_type: str | None = None
    pages: list[PageAnalysis] = Field(default_factory=list)
    canonical: DesignAssignmentCanonical | None = None
    stages_completed: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    quality_gates: list[QualityGateResult] = Field(default_factory=list)
    artifacts: dict[str, Path] = Field(default_factory=dict)
    stage_metrics: dict[str, Any] = Field(default_factory=dict)
