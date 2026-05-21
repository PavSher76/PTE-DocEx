"""PDF с текстовым слоем, bbox и OCR для сканов (ИСМ)."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

import fitz

from app.config import Settings
from app.ism.parse_pipeline import ParseResult, ParsedElement, structure_text
from app.services.ocr import extract_pdf_pages

logger = logging.getLogger(__name__)


@dataclass
class PageBlock:
    page: int
    text: str
    bbox: list[float] | None = None
    source: str = "text_layer"


def parse_pdf_with_layout(path, settings: Settings, *, filename: str) -> ParseResult:
    blocks = _extract_pdf_blocks(path, settings)
    full_text = "\n\n".join(b.text for b in blocks if b.text.strip())
    result = structure_text(full_text, filename=filename)
    result.metadata["pdf_blocks"] = len(blocks)
    result.metadata["ocr_used"] = any(b.source == "ocr" for b in blocks)

    for block in blocks:
        if len(block.text.strip()) < 8:
            continue
        result.elements.append(
            ParsedElement(
                "paragraph",
                "",
                block.text.strip(),
                source_page=block.page,
                bbox=block.bbox,
                extra={"source": block.source},
            )
        )
    return result


def _extract_pdf_blocks(path, settings: Settings) -> list[PageBlock]:
    blocks: list[PageBlock] = []
    try:
        doc = fitz.open(path)
    except Exception as exc:
        raise RuntimeError(f"Не удалось открыть PDF: {path.name}") from exc

    text_chars = 0
    try:
        for page_no, page in enumerate(doc, start=1):
            dict_blocks = page.get_text("dict", sort=True).get("blocks", [])
            page_text_parts: list[str] = []
            for block in dict_blocks:
                if block.get("type") != 0:
                    continue
                lines = block.get("lines", [])
                line_texts = []
                for line in lines:
                    spans = line.get("spans", [])
                    span_text = "".join(s.get("text", "") for s in spans)
                    if span_text.strip():
                        line_texts.append(span_text.strip())
                if not line_texts:
                    continue
                paragraph = " ".join(line_texts)
                page_text_parts.append(paragraph)
                bbox = block.get("bbox")
                blocks.append(
                    PageBlock(
                        page=page_no,
                        text=paragraph,
                        bbox=list(bbox) if bbox else None,
                        source="text_layer",
                    )
                )
            text_chars += sum(len(p) for p in page_text_parts)
    finally:
        doc.close()

    if text_chars >= settings.ocr_min_text_layer_chars:
        return blocks

    logger.info("ISM PDF %s: мало текста (%s), OCR", path.name, text_chars)
    blocks.clear()
    for page in extract_pdf_pages(path, settings, use_text_layer=False):
        if page.text.strip():
            blocks.append(PageBlock(page=page.page, text=page.text.strip(), source="ocr"))
    return blocks
