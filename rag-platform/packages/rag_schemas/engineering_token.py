from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

from rag_schemas.enums import DocumentStage, ElementType, TokenQuality


class EngineeringTokenPayload(BaseModel):
    """Канонический payload инженерного токена (PostgreSQL + Qdrant)."""

    token_id: UUID
    project_id: str
    document_id: UUID
    version_id: UUID
    stage: DocumentStage | None = None
    discipline: str | None = None
    document_code: str | None = None
    sheet_number: str | None = None
    page_number: int | None = None
    element_type: ElementType
    text: str
    bbox: list[float] | None = Field(default=None, min_length=4, max_length=4)
    source_uri: str
    revision: str | None = None
    status: str | None = None
    ntd_refs: list[str] = Field(default_factory=list)
    requirement_refs: list[str] = Field(default_factory=list)
    parent_token_id: UUID | None = None
    quality: TokenQuality = TokenQuality.COMPLETE
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
