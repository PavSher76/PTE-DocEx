"""Pydantic-схемы API модуля Документы ИСМ."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class IsmProcessRead(BaseModel):
    id: str
    process_code: str
    process_name: str
    owner: str
    description: str
    parent_process_id: str | None = None
    related_disciplines: list[str] = Field(default_factory=list)
    created_at: datetime | None = None


class IsmProcessCreate(BaseModel):
    process_code: str = Field(min_length=2, max_length=64)
    process_name: str = Field(min_length=1, max_length=512)
    owner: str = "ИСМ"
    description: str = ""
    parent_process_id: str | None = None
    related_disciplines: list[str] = Field(default_factory=list)


class IsmProcessUpdate(BaseModel):
    process_name: str | None = None
    owner: str | None = None
    description: str | None = None
    parent_process_id: str | None = None
    related_disciplines: list[str] | None = None


class IsmDocumentRead(BaseModel):
    document_id: str
    ism_process_id: str | None = None
    document_type: str
    title: str
    code: str
    revision: str
    status: str
    owner: str
    discipline: str | None = None
    related_processes: list[str] = Field(default_factory=list)
    related_documents: list[str] = Field(default_factory=list)
    batch_id: str | None = None
    filename: str | None = None
    file_type: str | None = None
    job_status: str | None = None
    job_progress: int = 0
    tokens_count: int = 0
    interfaces_count: int = 0
    review_status: str = "pending"
    created_at: datetime | None = None


class IsmDocumentDetailRead(IsmDocumentRead):
    requirements: list[dict[str, Any]] = Field(default_factory=list)
    interfaces: list[dict[str, Any]] = Field(default_factory=list)
    elements: list[dict[str, Any]] = Field(default_factory=list)
    rag_tokens_sample: list[dict[str, Any]] = Field(default_factory=list)
    ai_summary: str = ""
    parse_raw_json: dict[str, Any] | None = None


class IsmBatchUploadResponse(BaseModel):
    batch_id: str
    documents_total: int
    jobs_queued: int
    message: str


class IsmQueueItemRead(BaseModel):
    job_id: str
    document_id: str
    batch_id: str | None
    filename: str
    document_code: str
    status: str
    stage: str | None
    progress: int
    error_message: str | None = None
    created_at: datetime | None = None


class IsmQueueDashboardRead(BaseModel):
    batch_id: str | None = None
    total: int = 0
    by_status: dict[str, int] = Field(default_factory=dict)
    items: list[IsmQueueItemRead] = Field(default_factory=list)


class IsmGraphNode(BaseModel):
    id: str
    node_type: str
    label: str
    meta: dict[str, Any] = Field(default_factory=dict)


class IsmGraphEdge(BaseModel):
    id: str
    source: str
    target: str
    link_type: str
    label: str = ""
    confidence: float = 0.5


class IsmGraphRead(BaseModel):
    nodes: list[IsmGraphNode] = Field(default_factory=list)
    edges: list[IsmGraphEdge] = Field(default_factory=list)


class IsmErrorRead(BaseModel):
    id: str
    document_id: str
    job_id: str | None
    filename: str
    error_type: str
    message: str
    created_at: datetime | None = None


class IsmReviewUpdate(BaseModel):
    review_status: str = Field(pattern="^(pending|approved|rejected)$")
    review_notes: str = ""


class IsmBatchReportRead(BaseModel):
    batch_id: str
    report: dict[str, Any] = Field(default_factory=dict)


class IsmReviewQueueRead(BaseModel):
    batch_id: str
    items: list[IsmDocumentRead] = Field(default_factory=list)
