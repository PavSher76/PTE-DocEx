from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

LayoutBlockType = Literal[
    "heading",
    "paragraph",
    "table",
    "key_value",
    "signature",
    "footer",
    "header",
    "appendix",
]


class LayoutBlock(BaseModel):
    block_id: str
    block_type: LayoutBlockType
    page_number: int
    bbox: list[float]
    text: str
    confidence: float = 0.0
    metadata: dict = Field(default_factory=dict)


class PageAnalysis(BaseModel):
    page_number: int
    has_text_layer: bool
    text_quality_score: float
    image_required_for_ocr: bool
    rotation_angle: float = 0.0
    detected_language: str = "ru"
    pdf_type: Literal["born_digital", "raster", "mixed"] = "born_digital"
    blocks: list[LayoutBlock] = Field(default_factory=list)
