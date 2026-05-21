"""Индексация листов чертежей в PostgreSQL и Qdrant (Sprint 3)."""

from __future__ import annotations

from uuid import UUID

from rag_drawings.extractor import DrawingSheetExtractor
from rag_embeddings.dense import DenseEmbedder
from rag_embeddings.sparse import SparseEmbedder
from rag_storage.config import Settings
from rag_storage.minio_client import MinioStorage
from rag_storage.models import Document, DocumentElement, DocumentPage, DocumentVersion, EngineeringToken
from rag_storage.collections import drawings_collection_for
from rag_storage.qdrant_client import QdrantStore
from pathlib import Path
from sqlalchemy import select
from sqlalchemy.orm import Session


def index_drawings_for_pdf(
    session: Session,
    *,
    pdf_path: Path,
    document: Document,
    version: DocumentVersion,
    project_id: str,
    source_uri: str,
    settings: Settings,
) -> int:
    storage = MinioStorage(settings)
    extractor = DrawingSheetExtractor(settings)

    def upload_image(png_bytes: bytes, page_number: int) -> str:
        return storage.upload_page_image(
            png_bytes,
            project_id=project_id,
            document_id=document.id,
            version_id=version.id,
            page_number=page_number,
        )

    extraction = extractor.extract_from_pdf(pdf_path, upload_image=upload_image)
    if not extraction.pages:
        return 0

    dense = DenseEmbedder(settings)
    sparse = SparseEmbedder()
    qdrant = QdrantStore(settings)
    drawings_collection = drawings_collection_for(document, settings)
    qdrant.ensure_collections(dense.dimension)
    qdrant.delete_by_document_version(drawings_collection, version.id)

    tokens_indexed = 0
    for page_result in extraction.pages:
        page_row = DocumentPage(
            version_id=version.id,
            page_number=page_result.page_number,
            sheet_number=page_result.sheet_number,
            width=page_result.width,
            height=page_result.height,
            image_uri=page_result.image_uri,
        )
        session.add(page_row)
        session.flush()

        order = 0
        for zone_token in page_result.zone_tokens:
            order += 1
            element = DocumentElement(
                page_id=page_row.id,
                element_type=zone_token.element_type,
                text=zone_token.text,
                bbox=zone_token.bbox,
                reading_order=order,
                raw_metadata={
                    "zone": zone_token.zone_name,
                    "sheet_format": page_result.sheet_format,
                    **zone_token.metadata,
                },
            )
            session.add(element)

            token_row = EngineeringToken(
                id=zone_token.token_id,
                project_id=project_id,
                document_id=document.id,
                version_id=version.id,
                page_id=page_row.id,
                page_number=page_result.page_number,
                sheet_number=page_result.sheet_number,
                element_type=zone_token.element_type,
                text=zone_token.text,
                bbox=zone_token.bbox,
                source_uri=page_result.image_uri or source_uri,
                stage=document.stage,
                discipline=document.discipline,
                document_code=document.document_code,
                quality=zone_token.quality,
                extra={
                    "zone": zone_token.zone_name,
                    "sheet_format": page_result.sheet_format,
                    "collection": "drawings",
                    **zone_token.metadata,
                },
            )
            session.add(token_row)

            dense_vector = dense.embed(zone_token.text)
            sparse_indices, sparse_values = sparse.embed(zone_token.text)
            qdrant.upsert_token(
                drawings_collection,
                token_id=zone_token.token_id,
                dense_vector=dense_vector,
                sparse_indices=sparse_indices,
                sparse_values=sparse_values,
                payload={
                    "project_id": project_id,
                    "document_id": str(document.id),
                    "version_id": str(version.id),
                    "page_id": str(page_row.id),
                    "document_name": document.name,
                    "document_code": document.document_code,
                    "page_number": page_result.page_number,
                    "sheet_number": page_result.sheet_number,
                    "element_type": zone_token.element_type,
                    "zone": zone_token.zone_name,
                    "text": zone_token.text[:4000],
                    "bbox": zone_token.bbox,
                    "source_uri": page_result.image_uri or source_uri,
                    "metadata": zone_token.metadata,
                },
            )
            tokens_indexed += 1
        session.flush()
    return tokens_indexed


def delete_drawing_pages_for_version(session: Session, version_id: UUID) -> None:
    pages = list(session.scalars(select(DocumentPage).where(DocumentPage.version_id == version_id)))
    for page in pages:
        session.query(DocumentElement).filter(DocumentElement.page_id == page.id).delete()
        session.delete(page)
