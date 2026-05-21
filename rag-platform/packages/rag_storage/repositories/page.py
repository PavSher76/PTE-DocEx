from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from rag_storage.models import Document, DocumentElement, DocumentPage, DocumentVersion, EngineeringToken, ProcessingJob


class PageRepository:
    def __init__(self, session: Session):
        self._session = session

    def get_page_for_document(
        self, document_id: UUID, page_number: int
    ) -> tuple[DocumentPage, DocumentVersion, Document] | None:
        version = self._session.scalar(
            select(DocumentVersion)
            .join(Document)
            .where(Document.id == document_id, DocumentVersion.is_current.is_(True))
            .options(joinedload(DocumentVersion.document))
            .order_by(DocumentVersion.created_at.desc())
        )
        if version is None:
            version = self._session.scalar(
                select(DocumentVersion)
                .join(Document)
                .where(Document.id == document_id)
                .options(joinedload(DocumentVersion.document))
                .order_by(DocumentVersion.created_at.desc())
            )
        if version is None:
            return None
        page = self._session.scalar(
            select(DocumentPage).where(
                DocumentPage.version_id == version.id,
                DocumentPage.page_number == page_number,
            )
        )
        if page is None:
            return None
        return page, version, version.document

    def list_elements(self, page_id: UUID) -> list[DocumentElement]:
        return list(
            self._session.scalars(
                select(DocumentElement)
                .where(DocumentElement.page_id == page_id)
                .order_by(DocumentElement.reading_order)
            )
        )

    def list_drawing_tokens(self, page_id: UUID) -> list[EngineeringToken]:
        return list(
            self._session.scalars(
                select(EngineeringToken)
                .where(EngineeringToken.page_id == page_id)
                .order_by(EngineeringToken.page_number)
            )
        )

    def get_latest_version_id(self, document_id: UUID) -> UUID | None:
        job = self._session.scalar(
            select(ProcessingJob)
            .where(ProcessingJob.document_id == document_id)
            .order_by(ProcessingJob.created_at.desc())
        )
        return job.version_id if job else None
