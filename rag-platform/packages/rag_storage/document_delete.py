"""Полное удаление документа: Qdrant, MinIO, PostgreSQL."""

from __future__ import annotations

import logging
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.orm import Session, selectinload

from rag_storage.collections import drawings_collection_for, text_collection_for
from rag_storage.config import Settings
from rag_storage.minio_client import MinioStorage
from rag_storage.models import (
    Document,
    DocumentElement,
    DocumentPage,
    DocumentVersion,
    EngineeringToken,
    ProcessingJob,
    Requirement,
    SourceFile,
)
from rag_storage.qdrant_client import QdrantStore
from rag_storage.repositories.token import TokenRepository

logger = logging.getLogger("rag.document_delete")


def delete_document_completely(session: Session, document_id: UUID, settings: Settings) -> bool:
    document = session.scalar(
        select(Document)
        .where(Document.id == document_id)
        .options(selectinload(Document.versions).selectinload(DocumentVersion.source_files))
        .options(selectinload(Document.versions).selectinload(DocumentVersion.jobs))
        .options(selectinload(Document.versions).selectinload(DocumentVersion.pages))
    )
    if document is None:
        return False

    storage = MinioStorage(settings)
    qdrant = QdrantStore(settings)
    text_collection = text_collection_for(document, settings)
    drawings_collection = drawings_collection_for(document, settings)
    visual_collection = getattr(settings, "qdrant_collection_drawings_visual", "project_drawings_visual")

    version_ids = [v.id for v in document.versions]
    for version in document.versions:
        for collection in (text_collection, drawings_collection, visual_collection):
            try:
                qdrant.delete_by_document_version(collection, version.id)
            except Exception as exc:
                logger.warning(
                    "Qdrant delete doc=%s version=%s collection=%s: %s",
                    document_id,
                    version.id,
                    collection,
                    exc,
                )
        try:
            qdrant.delete_by_document_id(text_collection, document_id)
            qdrant.delete_by_document_id(drawings_collection, document_id)
        except Exception:
            pass

        _delete_storage_uris(storage, version)
        TokenRepository(session).delete_by_version(version.id)
        _delete_pages_and_elements(session, version.id, storage)
        session.execute(delete(ProcessingJob).where(ProcessingJob.version_id == version.id))

    session.execute(delete(Requirement).where(Requirement.document_id == document_id))
    session.execute(delete(EngineeringToken).where(EngineeringToken.document_id == document_id))
    session.execute(delete(ProcessingJob).where(ProcessingJob.document_id == document_id))
    if version_ids:
        session.execute(delete(SourceFile).where(SourceFile.version_id.in_(version_ids)))
    session.execute(delete(DocumentVersion).where(DocumentVersion.document_id == document_id))
    session.delete(document)
    session.flush()
    logger.info("Удалён документ RAG document_id=%s versions=%s", document_id, len(version_ids))
    return True


def _delete_storage_uris(storage: MinioStorage, version: DocumentVersion) -> None:
    for source in version.source_files:
        for uri in (source.storage_uri, source.parser_output_uri):
            if uri:
                storage.delete_uri(uri)
def _delete_pages_and_elements(session: Session, version_id: UUID, storage: MinioStorage) -> None:
    pages = list(session.scalars(select(DocumentPage).where(DocumentPage.version_id == version_id)))
    for page in pages:
        if page.image_uri:
            storage.delete_uri(page.image_uri)
        session.execute(delete(DocumentElement).where(DocumentElement.page_id == page.id))
        session.delete(page)
