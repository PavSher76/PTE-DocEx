"""Схемы HTTP API для персистентных профилей контекста проекта."""

from __future__ import annotations

import re
from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from app.project_context.ai_bundle import InvestmentProjectPackage

# Шифр проекта в стиле внутренних номеров (латиница/кириллица, цифры, точка, дефис, подчёркивание).
_PROJECT_CIPHER_RE = re.compile(r"^[a-zA-Z0-9\u0400-\u04FF][a-zA-Z0-9\u0400-\u04FF._\-]{0,127}$")


class ProjectProfileSummary(BaseModel):
    id: int
    project_cipher: str
    name: str
    primary_schema_binding: str
    updated_at: datetime


class ProjectProfileCreate(BaseModel):
    project_cipher: str = Field(min_length=1, max_length=128)
    name: str = Field(min_length=1, max_length=512)
    description: str = ""
    primary_schema_binding: str = Field(default="design_assignment_01_00", max_length=64)
    package: InvestmentProjectPackage

    @field_validator("project_cipher")
    @classmethod
    def project_cipher_format(cls, value: str) -> str:
        v = value.strip()
        if not v:
            raise ValueError("Шифр проекта не может быть пустым.")
        if not _PROJECT_CIPHER_RE.fullmatch(v):
            raise ValueError(
                "Шифр проекта: 1–128 символов; допускаются латиница и кириллица, цифры, «.», «-», «_»; "
                "первый символ — буква или цифра (не точка и не дефис). Пример: 3D01-0036-ТУГН.24.2144У-П-01."
            )
        return v


class ProjectProfileUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=512)
    description: str | None = None
    primary_schema_binding: str | None = Field(default=None, max_length=64)
    package: InvestmentProjectPackage | None = None


class ProjectProfileRead(BaseModel):
    id: int
    project_cipher: str
    name: str
    description: str
    primary_schema_binding: str
    package: InvestmentProjectPackage
    created_at: datetime
    updated_at: datetime


class ProjectContextChatTurn(BaseModel):
    role: str = Field(pattern=r"^(user|assistant)$")
    content: str = Field(min_length=1)


class ProjectContextChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=8000)
    history: list[ProjectContextChatTurn] = Field(default_factory=list)
    document_text: str | None = Field(default=None, max_length=200_000)
    ollama_model: str | None = Field(default=None, max_length=128)
    chat_prompt: str | None = Field(default=None, max_length=12_000)


class ProjectContextDocumentIngestResponse(BaseModel):
    filename: str
    extracted_text: str
    char_count: int


class ProjectContextChatResponse(BaseModel):
    reply: str
    changes_summary: str
    suggested_package: InvestmentProjectPackage | None = None
    package_valid: bool = True
    ollama_model: str
    ollama_prompt: str
