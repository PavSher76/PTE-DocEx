from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from rag_schemas.enums import JobStatus
from rag_schemas.engineering_token import EngineeringTokenPayload


class DocumentUploadResponse(BaseModel):
    document_id: UUID
    version_id: UUID
    source_file_id: UUID
    job_id: UUID
    status: JobStatus
    message: str = "Файл загружен, обработка поставлена в очередь"


class DocumentRead(BaseModel):
    id: UUID
    project_id: str
    name: str
    document_code: str | None
    stage: str | None
    discipline: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProcessingJobRead(BaseModel):
    id: UUID
    document_id: UUID
    version_id: UUID
    status: JobStatus
    stage: str | None
    error_message: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class DocumentStatusResponse(BaseModel):
    document_id: UUID
    version_id: UUID
    job: ProcessingJobRead
    tokens_count: int = 0


class DocumentTokensResponse(BaseModel):
    document_id: UUID
    version_id: UUID
    total: int
    items: list[EngineeringTokenPayload]
