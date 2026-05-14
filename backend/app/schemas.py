from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field

Status = Literal["OK", "Требует проверки", "Критично"]


class HealthResponse(BaseModel):
    status: str
    app: str


class CorrespondenceRequest(BaseModel):
    text: str = Field(min_length=1, max_length=50000)
    terminology: list[str] = Field(default_factory=list)
    check_prompt: str | None = None
    business_context: str | None = None
    strictness: Literal["standard", "strict", "critical"] = "standard"


class LanguageIssue(BaseModel):
    message: str
    short_message: str | None = None
    offset: int | None = None
    length: int | None = None
    context: str | None = None
    rule_id: str | None = None
    category: str | None = None
    replacements: list[str] = Field(default_factory=list)
    severity: Literal["info", "warning", "critical"] = "warning"
    accepted: bool = True
    reason: str | None = None


class StyleAssessment(BaseModel):
    status: Status = "Требует проверки"
    tone: str = "Не оценено"
    ethics: str = "Не оценено"
    terminology: str = "Не оценено"
    recommendations: list[str] = Field(default_factory=list)


class CorrespondenceResponse(BaseModel):
    id: int
    status: Status
    source_text: str
    languagetool_report: dict[str, Any]
    ollama_prompt: str
    language_tool_matches: list[LanguageIssue]
    filtered_matches: list[LanguageIssue]
    style_assessment: StyleAssessment
    created_at: datetime


class PageComparison(BaseModel):
    page: int
    similarity: float
    status: Status
    pdf_text: str
    editable_text: str
    differences: list[str] = Field(default_factory=list)


class DocumentComparisonResponse(BaseModel):
    id: int
    status: Status
    similarity: float
    conclusion: str
    page_results: list[PageComparison]
    created_at: datetime


class ErrorResponse(BaseModel):
    detail: str | dict[str, Any]
