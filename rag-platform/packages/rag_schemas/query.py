from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

from rag_schemas.enums import DocumentStage


class SearchFilters(BaseModel):
    stage: DocumentStage | None = None
    discipline: str | None = None
    document_code: str | None = None
    revision: str | None = None
    status: str | None = None
    element_type: str | None = None
    page_number: int | None = None


class SearchRequest(BaseModel):
    project_id: str
    query: str = Field(min_length=1)
    filters: SearchFilters = Field(default_factory=SearchFilters)
    top_k: int = Field(default=10, ge=1, le=50)
    debug: bool = False


class NtdSearchRequest(BaseModel):
    project_id: str
    ntd_ref: str = Field(min_length=2, description="СП 60.13330, ГОСТ 21.110-2013 и т.п.")
    filters: SearchFilters = Field(default_factory=SearchFilters)
    top_k: int = Field(default=10, ge=1, le=50)


class QueryRequest(SearchRequest):
    """Запрос с генерацией ответа LLM (этап 8)."""

    use_llm: bool = True
    model: str | None = None


class SearchHit(BaseModel):
    token_id: UUID
    score: float
    text: str
    document_id: UUID
    document_name: str | None = None
    document_code: str | None = None
    page_number: int | None = None
    sheet_number: str | None = None
    element_type: str
    bbox: list[float] | None = None
    source_uri: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class QueryResponse(BaseModel):
    answer: str
    hits: list[SearchHit]
    citations: list[SearchHit]
    debug_chunks: list[SearchHit] | None = None
    llm_used: bool = False
    warnings: list[str] = Field(default_factory=list)
