from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from rag_drawings.extractor import highlight_bboxes_png
from rag_schemas.drawing import BboxOverlay, PageListItem, PagePreviewResponse
from rag_storage.config import get_settings
from rag_storage.db import get_db_session
from rag_storage.minio_client import MinioStorage
from rag_storage.models import Document, DocumentPage, EngineeringToken
from rag_storage.repositories.page import PageRepository

router = APIRouter(prefix="/documents", tags=["drawings"])


def get_db():
    yield from get_db_session()


@router.get("/{document_id}/pages", response_model=list[PageListItem])
def list_document_pages(document_id: UUID, db: Session = Depends(get_db)) -> list[PageListItem]:
    document = db.get(Document, document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Документ не найден.")
    version_id = PageRepository(db).get_latest_version_id(document_id)
    if version_id is None:
        return []
    rows = db.execute(
        select(
            DocumentPage.page_number,
            DocumentPage.sheet_number,
            DocumentPage.width,
            DocumentPage.height,
            DocumentPage.image_uri,
            func.count(EngineeringToken.id),
        )
        .outerjoin(EngineeringToken, EngineeringToken.page_id == DocumentPage.id)
        .where(DocumentPage.version_id == version_id)
        .group_by(
            DocumentPage.id,
            DocumentPage.page_number,
            DocumentPage.sheet_number,
            DocumentPage.width,
            DocumentPage.height,
            DocumentPage.image_uri,
        )
        .order_by(DocumentPage.page_number)
    ).all()
    return [
        PageListItem(
            page_number=row[0],
            sheet_number=row[1],
            width=row[2],
            height=row[3],
            has_image=bool(row[4]),
            token_count=int(row[5] or 0),
        )
        for row in rows
    ]


@router.get("/{document_id}/pages/{page_number}/preview", response_model=PagePreviewResponse)
def page_preview(
    document_id: UUID,
    page_number: int,
    highlight: bool = Query(default=False),
    db: Session = Depends(get_db),
) -> PagePreviewResponse:
    repo = PageRepository(db)
    loaded = repo.get_page_for_document(document_id, page_number)
    if loaded is None:
        raise HTTPException(status_code=404, detail="Страница не найдена.")
    page, _version, _document = loaded
    settings = get_settings()
    storage = MinioStorage(settings)

    tokens = repo.list_drawing_tokens(page.id)
    overlays = [
        BboxOverlay(
            token_id=token.id,
            label=str((token.extra or {}).get("zone", token.element_type)),
            element_type=token.element_type,
            bbox=token.bbox or [],
            text_preview=(token.text or "")[:200],
        )
        for token in tokens
        if token.bbox
    ]

    image_url = None
    if page.image_uri:
        try:
            image_url = storage.generate_presigned_url(page.image_uri)
        except Exception:
            image_url = None

    return PagePreviewResponse(
        document_id=document_id,
        page_number=page_number,
        width=page.width,
        height=page.height,
        sheet_number=page.sheet_number,
        image_uri=page.image_uri,
        image_url=image_url,
        overlays=overlays,
    )


@router.get("/{document_id}/pages/{page_number}/preview/image")
def page_preview_image(
    document_id: UUID,
    page_number: int,
    highlight: bool = Query(default=False),
    token_id: UUID | None = Query(default=None),
    db: Session = Depends(get_db),
) -> Response:
    repo = PageRepository(db)
    loaded = repo.get_page_for_document(document_id, page_number)
    if loaded is None:
        raise HTTPException(status_code=404, detail="Страница не найдена.")
    page, _, _ = loaded
    if not page.image_uri:
        raise HTTPException(status_code=404, detail="Изображение страницы не сохранено.")

    settings = get_settings()
    png_bytes = MinioStorage(settings).download_bytes(page.image_uri)

    if highlight:
        tokens = repo.list_drawing_tokens(page.id)
        boxes = []
        for token in tokens:
            if token_id and token.id != token_id:
                continue
            if not token.bbox:
                continue
            boxes.append(
                {
                    "bbox": token.bbox,
                    "label": (token.extra or {}).get("zone", token.element_type),
                    "element_type": token.element_type,
                }
            )
        if boxes:
            png_bytes = highlight_bboxes_png(png_bytes, boxes)

    return Response(content=png_bytes, media_type="image/png")

