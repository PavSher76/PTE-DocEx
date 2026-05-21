"""Детекция типа PDF: born-digital / raster / mixed."""

from __future__ import annotations

from pathlib import Path

from app.config import Settings
from app.models.layout import PageAnalysis
from app.ocr.extract import PageText, extract_pages


def detect_pdf_type(pdf_path: Path, settings: Settings) -> tuple[str, list[PageAnalysis]]:
    pages_text = extract_pages(pdf_path, settings)
    analyses: list[PageAnalysis] = []
    raster_count = 0
    digital_count = 0

    for pt in pages_text:
        has_layer = pt.source == "pymupdf_text_layer" and len(pt.text.strip()) > 20
        quality = _text_quality(pt.text)
        needs_ocr = not has_layer or quality < 0.35
        if needs_ocr:
            raster_count += 1
            page_type = "raster"
        else:
            digital_count += 1
            page_type = "born_digital"

        analyses.append(
            PageAnalysis(
                page_number=pt.page,
                has_text_layer=has_layer,
                text_quality_score=quality,
                image_required_for_ocr=needs_ocr,
                rotation_angle=0.0,
                detected_language=_detect_language(pt.text),
                pdf_type=page_type,
            )
        )

    if raster_count and digital_count:
        overall = "mixed"
    elif raster_count:
        overall = "raster"
    else:
        overall = "born_digital"

    for a in analyses:
        a.pdf_type = overall  # type: ignore[assignment]

    return overall, analyses


def pages_to_layout_blocks(pages_text: list[PageText]) -> list:
    from app.models.layout import LayoutBlock

    blocks: list[LayoutBlock] = []
    for pt in pages_text:
        if pt.blocks:
            for i, b in enumerate(pt.blocks):
                bbox = b.get("bbox") or [0, 0, 0, 0]
                blocks.append(
                    LayoutBlock(
                        block_id=f"p{pt.page}-b{i}",
                        block_type="paragraph",
                        page_number=pt.page,
                        bbox=[float(x) for x in bbox[:4]],
                        text=b.get("text", ""),
                        confidence=pt.confidence,
                    )
                )
        elif pt.text.strip():
            blocks.append(
                LayoutBlock(
                    block_id=f"p{pt.page}-full",
                    block_type="paragraph",
                    page_number=pt.page,
                    bbox=[0, 0, 0, 0],
                    text=pt.text,
                    confidence=pt.confidence,
                )
            )
    return blocks


def _text_quality(text: str) -> float:
    t = text.strip()
    if not t:
        return 0.0
    alnum = sum(1 for c in t if c.isalnum())
    return min(1.0, alnum / max(len(t), 1) * 1.4)


def _detect_language(text: str) -> str:
    cyr = sum(1 for c in text if "\u0400" <= c <= "\u04FF")
    lat = sum(1 for c in text if c.isascii() and c.isalpha())
    if cyr >= lat:
        return "ru"
    if lat > cyr:
        return "en"
    return "ru"
