"""SQLAlchemy-модели модуля Документы ИСМ."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Index, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def _uuid() -> str:
    return str(uuid.uuid4())


class IsmProcess(Base):
    __tablename__ = "ism_processes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    process_code: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    process_name: Mapped[str] = mapped_column(String(512))
    owner: Mapped[str] = mapped_column(String(128), default="ИСМ", index=True)
    description: Mapped[str] = mapped_column(Text, default="")
    parent_process_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("ism_processes.id"), nullable=True
    )
    related_disciplines: Mapped[list] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    documents: Mapped[list["IsmDocument"]] = relationship(back_populates="process")


class IsmUploadBatch(Base):
    __tablename__ = "ism_upload_batches"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    title: Mapped[str] = mapped_column(String(512), default="")
    project_cipher: Mapped[str | None] = mapped_column(String(128), nullable=True)
    comment: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(32), default="uploaded", index=True)
    ai_pipeline_status: Mapped[str] = mapped_column(String(32), default="pending")
    ai_pipeline_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    report_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    documents: Mapped[list[IsmDocument]] = relationship(back_populates="batch")


class IsmDocument(Base):
    __tablename__ = "ism_documents"
    __table_args__ = (
        Index("ix_ism_documents_code_status", "code", "status"),
        Index("ix_ism_documents_process_type", "ism_process_id", "document_type"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    ism_process_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("ism_processes.id"), nullable=True, index=True
    )
    batch_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("ism_upload_batches.id"), nullable=True, index=True
    )
    document_type: Mapped[str] = mapped_column(String(64), default="OTHER", index=True)
    title: Mapped[str] = mapped_column(String(512), default="")
    code: Mapped[str] = mapped_column(String(128), default="", index=True)
    revision: Mapped[str] = mapped_column(String(32), default="A", index=True)
    status: Mapped[str] = mapped_column(String(32), default="active", index=True)
    owner: Mapped[str] = mapped_column(String(128), default="ИСМ", index=True)
    discipline: Mapped[str | None] = mapped_column(String(32), nullable=True)
    related_processes: Mapped[list] = mapped_column(JSON, default=list)
    related_documents: Mapped[list] = mapped_column(JSON, default=list)
    parse_raw_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    ai_summary: Mapped[str] = mapped_column(Text, default="")
    ai_classification: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    review_status: Mapped[str] = mapped_column(String(32), default="pending", index=True)
    review_notes: Mapped[str] = mapped_column(Text, default="")
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    process: Mapped[IsmProcess | None] = relationship(back_populates="documents")
    batch: Mapped[IsmUploadBatch | None] = relationship(back_populates="documents")
    versions: Mapped[list[IsmDocumentVersion]] = relationship(back_populates="document")
    elements: Mapped[list[IsmDocumentElement]] = relationship(back_populates="document")
    requirements: Mapped[list[IsmRequirement]] = relationship(back_populates="document")
    jobs: Mapped[list[IsmProcessingJob]] = relationship(back_populates="document")
    rag_tokens: Mapped[list[IsmRagToken]] = relationship(back_populates="document")


class IsmDocumentVersion(Base):
    __tablename__ = "ism_document_versions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    document_id: Mapped[str] = mapped_column(String(36), ForeignKey("ism_documents.id"), index=True)
    version_number: Mapped[int] = mapped_column(Integer, default=1)
    revision: Mapped[str] = mapped_column(String(32), default="A")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    document: Mapped[IsmDocument] = relationship(back_populates="versions")
    files: Mapped[list[IsmDocumentFile]] = relationship(back_populates="version")


class IsmDocumentFile(Base):
    __tablename__ = "ism_document_files"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    document_id: Mapped[str] = mapped_column(String(36), ForeignKey("ism_documents.id"), index=True)
    version_id: Mapped[str] = mapped_column(String(36), ForeignKey("ism_document_versions.id"), index=True)
    filename: Mapped[str] = mapped_column(String(512))
    relative_path: Mapped[str] = mapped_column(String(1024), default="")
    file_type: Mapped[str] = mapped_column(String(16))
    size_bytes: Mapped[int] = mapped_column(Integer, default=0)
    storage_path: Mapped[str] = mapped_column(String(1024))

    version: Mapped[IsmDocumentVersion] = relationship(back_populates="files")


class IsmDocumentElement(Base):
    __tablename__ = "ism_document_elements"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    document_id: Mapped[str] = mapped_column(String(36), ForeignKey("ism_documents.id"), index=True)
    version_id: Mapped[str] = mapped_column(String(36), ForeignKey("ism_document_versions.id"), index=True)
    element_type: Mapped[str] = mapped_column(String(64), index=True)
    section: Mapped[str] = mapped_column(String(128), default="")
    text: Mapped[str] = mapped_column(Text)
    source_page: Mapped[int | None] = mapped_column(Integer, nullable=True)
    source_table: Mapped[str | None] = mapped_column(String(128), nullable=True)
    bbox: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    extra: Mapped[dict] = mapped_column(JSON, default=dict)

    document: Mapped[IsmDocument] = relationship(back_populates="elements")


class IsmRequirement(Base):
    __tablename__ = "ism_requirements"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    document_id: Mapped[str] = mapped_column(String(36), ForeignKey("ism_documents.id"), index=True)
    text: Mapped[str] = mapped_column(Text)
    section: Mapped[str] = mapped_column(String(128), default="")
    source_element_id: Mapped[str | None] = mapped_column(String(36), nullable=True)

    document: Mapped[IsmDocument] = relationship(back_populates="requirements")


class IsmInterface(Base):
    __tablename__ = "ism_interfaces"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    batch_id: Mapped[str | None] = mapped_column(String(36), index=True)
    source_document_id: Mapped[str] = mapped_column(String(36), ForeignKey("ism_documents.id"), index=True)
    target_document_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("ism_documents.id"), nullable=True
    )
    link_type: Mapped[str] = mapped_column(String(64), index=True)
    reference_text: Mapped[str] = mapped_column(Text, default="")
    target_discipline: Mapped[str | None] = mapped_column(String(32), nullable=True)
    target_document_code: Mapped[str | None] = mapped_column(String(128), nullable=True)
    confidence: Mapped[float] = mapped_column(Float, default=0.5)
    extra: Mapped[dict] = mapped_column(JSON, default=dict)


class IsmProcessingJob(Base):
    __tablename__ = "ism_processing_jobs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    document_id: Mapped[str] = mapped_column(String(36), ForeignKey("ism_documents.id"), index=True)
    batch_id: Mapped[str | None] = mapped_column(String(36), index=True)
    status: Mapped[str] = mapped_column(String(32), default="uploaded", index=True)
    stage: Mapped[str | None] = mapped_column(String(64), nullable=True)
    progress: Mapped[int] = mapped_column(Integer, default=0)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    rag_document_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    document: Mapped[IsmDocument] = relationship(back_populates="jobs")
    errors: Mapped[list[IsmProcessingError]] = relationship(back_populates="job")


class IsmProcessingError(Base):
    __tablename__ = "ism_processing_errors"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    job_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("ism_processing_jobs.id"), index=True)
    document_id: Mapped[str] = mapped_column(String(36), ForeignKey("ism_documents.id"), index=True)
    error_type: Mapped[str] = mapped_column(String(64), default="parse")
    message: Mapped[str] = mapped_column(Text)
    details: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    job: Mapped[IsmProcessingJob | None] = relationship(back_populates="errors")


class IsmRagToken(Base):
    __tablename__ = "ism_rag_tokens"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    document_id: Mapped[str] = mapped_column(String(36), ForeignKey("ism_documents.id"), index=True)
    process_id: Mapped[str | None] = mapped_column(String(36), nullable=True, index=True)
    document_code: Mapped[str] = mapped_column(String(128), default="")
    document_type: Mapped[str] = mapped_column(String(64), default="")
    revision: Mapped[str] = mapped_column(String(32), default="")
    section: Mapped[str] = mapped_column(String(128), default="")
    token_type: Mapped[str] = mapped_column(String(64), index=True)
    text: Mapped[str] = mapped_column(Text)
    source_page: Mapped[int | None] = mapped_column(Integer, nullable=True)
    source_table: Mapped[str | None] = mapped_column(String(128), nullable=True)
    bbox: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    related_documents: Mapped[list] = mapped_column(JSON, default=list)
    related_requirements: Mapped[list] = mapped_column(JSON, default=list)
    confidence: Mapped[float] = mapped_column(Float, default=0.9)
    qdrant_point_id: Mapped[str | None] = mapped_column(String(64), nullable=True)

    document: Mapped[IsmDocument] = relationship(back_populates="rag_tokens")
