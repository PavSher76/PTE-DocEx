from datetime import datetime
from enum import StrEnum

from sqlalchemy import DateTime, Enum, Float, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class CheckStatus(StrEnum):
    ok = "OK"
    review = "Требует проверки"
    critical = "Критично"


class CorrespondenceCheck(Base):
    __tablename__ = "correspondence_checks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    source_text: Mapped[str] = mapped_column(Text)
    status: Mapped[CheckStatus] = mapped_column(Enum(CheckStatus), default=CheckStatus.review)
    language_tool_matches: Mapped[list[dict]] = mapped_column(JSON, default=list)
    filtered_matches: Mapped[list[dict]] = mapped_column(JSON, default=list)
    style_assessment: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class DocumentComparison(Base):
    __tablename__ = "document_comparisons"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    pdf_filename: Mapped[str] = mapped_column(String(255))
    editable_filename: Mapped[str] = mapped_column(String(255))
    status: Mapped[CheckStatus] = mapped_column(Enum(CheckStatus), default=CheckStatus.review)
    similarity: Mapped[float] = mapped_column(Float, default=0.0)
    conclusion: Mapped[str] = mapped_column(Text)
    page_results: Mapped[list[dict]] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ProjectProfile(Base):
    """Персистентный контекст проекта (единый JSON-пакет + привязка к целевой схеме генерации)."""

    __tablename__ = "project_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    project_cipher: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(512))
    description: Mapped[str] = mapped_column(Text, default="")
    primary_schema_binding: Mapped[str] = mapped_column(String(64), default="design_assignment_01_00")
    context_payload: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
