from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class CheckStatus(StrEnum):
    PASSED = "passed"
    WARNING = "warning"
    FAILED = "failed"
    SKIPPED = "skipped"


class CheckResult(BaseModel):
    check_id: str
    title: str
    status: CheckStatus
    summary: str
    details: list[str] = Field(default_factory=list)
    evidence: list[dict[str, Any]] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)


class CheckReport(BaseModel):
    run_id: UUID
    project_id: str
    created_at: datetime
    overall_status: CheckStatus
    checks: list[CheckResult]
    summary: str
    stats: dict[str, int] = Field(default_factory=dict)

    def compute_stats(self) -> None:
        self.stats = {s.value: 0 for s in CheckStatus}
        for check in self.checks:
            self.stats[check.status.value] = self.stats.get(check.status.value, 0) + 1
        if self.stats.get(CheckStatus.FAILED.value, 0) > 0:
            self.overall_status = CheckStatus.FAILED
        elif self.stats.get(CheckStatus.WARNING.value, 0) > 0:
            self.overall_status = CheckStatus.WARNING
        else:
            self.overall_status = CheckStatus.PASSED
