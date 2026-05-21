from uuid import UUID

from pydantic import BaseModel, Field


class BboxOverlay(BaseModel):
    token_id: UUID | None = None
    label: str
    element_type: str
    bbox: list[float] = Field(min_length=4, max_length=4)
    text_preview: str = ""


class PagePreviewResponse(BaseModel):
    document_id: UUID
    page_number: int
    width: int | None = None
    height: int | None = None
    sheet_number: str | None = None
    image_uri: str | None = None
    image_url: str | None = None
    overlays: list[BboxOverlay] = Field(default_factory=list)


class PageListItem(BaseModel):
    page_number: int
    sheet_number: str | None = None
    width: int | None = None
    height: int | None = None
    has_image: bool = False
    token_count: int = 0
