"""Загрузка контекста проекта для проверок AI-NK."""

from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from rag_storage.models import (
    Document,
    DocumentPage,
    EngineeringToken,
    Project,
    Requirement,
)


@dataclass
class DocumentSnapshot:
    id: UUID
    name: str
    document_code: str | None
    stage: str | None
    discipline: str | None
    indexed: bool
    token_count: int


@dataclass
class ProjectCheckContext:
    project_id: str
    project_name: str
    documents: list[DocumentSnapshot] = field(default_factory=list)
    tokens: list[EngineeringToken] = field(default_factory=list)
    requirements: list[Requirement] = field(default_factory=list)
    pages: list[DocumentPage] = field(default_factory=list)

    @property
    def disciplines(self) -> set[str]:
        return {d.discipline for d in self.documents if d.discipline}

    @property
    def document_codes(self) -> set[str]:
        return {d.document_code for d in self.documents if d.document_code}

    @property
    def indexed_documents(self) -> list[DocumentSnapshot]:
        return [d for d in self.documents if d.indexed]


def load_project_context(session: Session, project_id: str) -> ProjectCheckContext:
    project = session.scalar(select(Project).where(Project.project_id == project_id))
    if project is None:
        raise ValueError(f"Проект {project_id} не найден")

    documents = list(
        session.scalars(select(Document).where(Document.project_uuid == project.id))
    )
    tokens = list(
        session.scalars(select(EngineeringToken).where(EngineeringToken.project_id == project_id))
    )
    requirements = list(
        session.scalars(select(Requirement).where(Requirement.project_id == project_id))
    )

    from rag_storage.models import ProcessingJob

    snapshots: list[DocumentSnapshot] = []
    for doc in documents:
        job = session.scalar(
            select(ProcessingJob)
            .where(ProcessingJob.document_id == doc.id)
            .order_by(ProcessingJob.created_at.desc())
        )
        token_count = sum(1 for t in tokens if t.document_id == doc.id)
        snapshots.append(
            DocumentSnapshot(
                id=doc.id,
                name=doc.name,
                document_code=doc.document_code,
                stage=doc.stage,
                discipline=doc.discipline,
                indexed=job is not None and job.status == "indexed",
                token_count=token_count,
            )
        )

    version_ids = {t.version_id for t in tokens}
    pages: list[DocumentPage] = []
    if version_ids:
        pages = list(
            session.scalars(select(DocumentPage).where(DocumentPage.version_id.in_(version_ids)))
        )

    return ProjectCheckContext(
        project_id=project_id,
        project_name=project.name,
        documents=snapshots,
        tokens=tokens,
        requirements=requirements,
        pages=pages,
    )
