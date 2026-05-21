from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from rag_aink.schemas import CheckReport


class PilotBootstrapResponse(BaseModel):
    project_id: str
    name: str
    created: bool
    message: str


class PilotRunRequest(BaseModel):
    check_ids: list[str] | None = None
    run_query: str | None = Field(
        default="Какие исходные данные требуются для раздела ТХ?",
        description="Демонстрационный RAG-запрос для пилота",
    )


class PilotSourceDataIssue(BaseModel):
    check_id: str
    summary: str
    details: list[str] = Field(default_factory=list)


class PilotRunResponse(BaseModel):
    project_id: str
    documents_count: int
    requirements_count: int
    check_report: CheckReport
    source_data_issues: list[PilotSourceDataIssue]
    query_answer: str | None = None
    markdown_url_hint: str
    run_id: UUID


class PilotFeedbackCreate(BaseModel):
    project_id: str
    source_type: str = Field(pattern=r"^(query|check|pilot_run)$")
    source_id: str | None = None
    rating: int = Field(ge=1, le=5)
    comment: str = ""
    lesson_tags: list[str] = Field(default_factory=list)


class PilotFeedbackRead(BaseModel):
    id: UUID
    project_id: str
    source_type: str
    source_id: str | None
    rating: int
    comment: str
    lesson_tags: list[str]
    created_at: datetime

    model_config = {"from_attributes": True}
