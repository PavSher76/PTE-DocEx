from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from uuid import UUID, uuid4

from rag_drawings.ocr import ZoneOcrResult, ocr_zone
from rag_drawings.renderer import RenderedPage, render_pdf_pages
from rag_drawings.stamp_parser import parse_stamp_text
from rag_drawings.zones import DEFAULT_DRAWING_ZONES, SheetZone, detect_sheet_format
from rag_schemas.enums import ElementType, TokenQuality
from rag_storage.config import Settings


@dataclass
class DrawingZoneToken:
    token_id: UUID
    page_number: int
    element_type: str
    zone_name: str
    text: str
    bbox: list[float]
    quality: str
    sheet_number: str | None = None
    metadata: dict = field(default_factory=dict)


@dataclass
class DrawingPageResult:
    page_number: int
    width: int
    height: int
    png_bytes: bytes
    image_uri: str | None
    sheet_format: str | None
    sheet_number: str | None
    is_drawing: bool
    zone_tokens: list[DrawingZoneToken] = field(default_factory=list)


@dataclass
class DrawingExtractionResult:
    pages: list[DrawingPageResult]
    drawing_page_count: int


class DrawingSheetExtractor:
    def __init__(self, settings: Settings):
        self._settings = settings
        self._zones = DEFAULT_DRAWING_ZONES

    def extract_from_pdf(
        self,
        path: Path,
        *,
        upload_image,
    ) -> DrawingExtractionResult:
        rendered = render_pdf_pages(path, dpi=self._settings.drawing_render_dpi)
        results: list[DrawingPageResult] = []
        drawing_count = 0

        for page in rendered:
            if not page.is_likely_drawing and not self._settings.drawing_process_all_pdf_pages:
                continue
            drawing_count += 1
            image_uri = upload_image(page.png_bytes, page.page_number)
            zone_tokens = self._ocr_page(page)
            sheet_number = None
            sheet_format = detect_sheet_format(page.width, page.height, self._settings.drawing_render_dpi)
            for token in zone_tokens:
                if token.zone_name == "stamp" and token.text:
                    stamp_meta = parse_stamp_text(token.text)
                    sheet_number = stamp_meta.get("sheet_number") or sheet_number
                    token.metadata.update(stamp_meta)
                    if stamp_meta.get("sheet_title"):
                        token.text = f"{token.text}\nНаименование: {stamp_meta['sheet_title']}"

            results.append(
                DrawingPageResult(
                    page_number=page.page_number,
                    width=page.width,
                    height=page.height,
                    png_bytes=page.png_bytes,
                    image_uri=image_uri,
                    sheet_format=sheet_format,
                    sheet_number=sheet_number,
                    is_drawing=page.is_likely_drawing,
                    zone_tokens=zone_tokens,
                )
            )
        return DrawingExtractionResult(pages=results, drawing_page_count=drawing_count)

    def _ocr_page(self, page: RenderedPage) -> list[DrawingZoneToken]:
        tokens: list[DrawingZoneToken] = []
        if not self._settings.drawing_ocr_enabled:
            return self._fallback_tokens(page)

        for zone in self._zones:
            ocr = ocr_zone(page.png_bytes, zone, lang=self._settings.ocr_language)
            text = ocr.text.strip()
            if not text and zone.name != "main_drawing":
                continue
            tokens.append(self._zone_to_token(page, zone, ocr))
        return tokens or self._fallback_tokens(page)

    def _zone_to_token(self, page: RenderedPage, zone: SheetZone, ocr: ZoneOcrResult) -> DrawingZoneToken:
        quality = TokenQuality.COMPLETE.value
        if not ocr.ocr_available:
            quality = TokenQuality.OCR_RISK.value
        elif ocr.confidence < 0.45 or len(ocr.text) < 4:
            quality = TokenQuality.WEAK.value
        element_type = zone.element_type
        if zone.name == "stamp":
            element_type = ElementType.STAMP.value
        elif zone.name == "specification":
            element_type = ElementType.SPECIFICATION.value
        elif zone.name == "notes":
            element_type = ElementType.NOTE.value
        elif zone.name == "main_drawing":
            element_type = ElementType.DRAWING_ZONE.value

        return DrawingZoneToken(
            token_id=uuid4(),
            page_number=page.page_number,
            element_type=element_type,
            zone_name=zone.name,
            text=ocr.text,
            bbox=ocr.bbox,
            quality=quality,
            metadata={"zone": zone.name, "ocr_confidence": ocr.confidence},
        )

    def _fallback_tokens(self, page: RenderedPage) -> list[DrawingZoneToken]:
        return [
            DrawingZoneToken(
                token_id=uuid4(),
                page_number=page.page_number,
                element_type=ElementType.DRAWING_ZONE.value,
                zone_name="main_drawing",
                text=f"Лист чертежа {page.page_number} (OCR недоступен, изображение сохранено).",
                bbox=DEFAULT_DRAWING_ZONES[-1].bbox_list(page.width, page.height),
                quality=TokenQuality.OCR_RISK.value,
                metadata={"ocr": False},
            )
        ]


def highlight_bboxes_png(png_bytes: bytes, bboxes: list[dict], *, stroke: str = "#e11d48") -> bytes:
    """Рисует рамки bbox на копии изображения для preview."""
    from io import BytesIO

    from PIL import Image, ImageDraw

    image = Image.open(BytesIO(png_bytes)).convert("RGB")
    draw = ImageDraw.Draw(image)
    for item in bboxes:
        bbox = item.get("bbox") or []
        if len(bbox) != 4:
            continue
        draw.rectangle(bbox, outline=stroke, width=4)
        label = item.get("label") or item.get("element_type") or ""
        if label:
            draw.text((bbox[0] + 4, bbox[1] + 4), label[:40], fill=stroke)
    out = BytesIO()
    image.save(out, format="PNG")
    return out.getvalue()
