from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class JobCreatedResponse(BaseModel):
    job_id: UUID
    status: str


class JobStatusResponse(BaseModel):
    job_id: UUID
    status: str
    pdf_type: str | None = None
    stages_completed: list[str] = Field(default_factory=list)
    quality_gates: list[dict] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    artifacts: list[str] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime


class ValidationReportResponse(BaseModel):
    valid: bool
    errors: list[str] = Field(default_factory=list)
    missing_required_fields: list[str] = Field(default_factory=list)
