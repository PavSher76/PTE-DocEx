from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ProjectCreate(BaseModel):
    project_id: str = Field(min_length=1, max_length=64, description="Внешний код проекта, напр. PTE-25-450")
    name: str = Field(min_length=1, max_length=512)
    description: str = ""


class ProjectRead(BaseModel):
    id: UUID
    project_id: str
    name: str
    description: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
