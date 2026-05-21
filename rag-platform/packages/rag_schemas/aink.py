from uuid import UUID

from pydantic import BaseModel, Field

from rag_aink.schemas import CheckReport, CheckResult


class RunChecksRequest(BaseModel):
    check_ids: list[str] | None = Field(
        default=None,
        description="Список id проверок; null — все зарегистрированные",
    )


class RunChecksResponse(BaseModel):
    run_id: UUID
    report: CheckReport
    markdown_url_hint: str = "/projects/{project_id}/checks/{run_id}/report.md"


class CheckRunSummary(BaseModel):
    run_id: UUID
    project_id: str
    overall_status: str
    created_at: str
    checks_count: int


class RequirementTraceResponse(BaseModel):
    requirement_id: UUID
    requirement_text: str
    related_hits: list[dict]
    status: str
