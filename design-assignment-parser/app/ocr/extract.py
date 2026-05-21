"""Извлечение текста: PyMuPDF → OCR (как PTE-DocEx переписка)."""

from __future__ import annotations

import math
import re
from dataclasses import dataclass
from pathlib import Path

from app.config import Settings

TOKEN_RE = re.compile(r"[\w\u0400-\u04FF]+", re.UNICODE)


@dataclass
class PageText:
    page: int
    text: str
    source: str
    confidence: float = 1.0
    blocks: list[dict] | None = None


def extract_pages(pdf_path: Path, settings: Settings) -> list[PageText]:
    pages = _extract_fitz(pdf_path)
    if _total_chars(pages) < settings.ocr_min_text_layer_chars:
        pages = _extract_ocr(pdf_path, settings)
    return pages


def _total_chars(pages: list[PageText]) -> int:
    return sum(len(p.text.strip()) for p in pages)


def _extract_fitz(pdf_path: Path) -> list[PageText]:
    import fitz

    doc = fitz.open(pdf_path)
    pages: list[PageText] = []
    try:
        for i, page in enumerate(doc, start=1):
            blocks_raw = page.get_text("dict", sort=True).get("blocks", [])
            blocks: list[dict] = []
            parts: list[str] = []
            for block in blocks_raw:
                if block.get("type") != 0:
                    continue
                lines = []
                for line in block.get("lines", []):
                    span_text = "".join(span.get("text", "") for span in line.get("spans", []))
                    lines.append(span_text)
                text = "\n".join(lines).strip()
                if not text:
                    continue
                parts.append(text)
                blocks.append({"bbox": block.get("bbox"), "text": text, "type": "paragraph"})
            full = _cleanup("\n".join(parts))
            pages.append(
                PageText(
                    page=i,
                    text=full,
                    source="pymupdf_text_layer",
                    confidence=1.0 if full.strip() else 0.0,
                    blocks=blocks,
                )
            )
    finally:
        doc.close()
    return pages


def _extract_ocr(pdf_path: Path, settings: Settings) -> list[PageText]:
    import pytesseract
    from pdf2image import convert_from_path
    from PIL import ImageFilter, ImageOps

    images = convert_from_path(pdf_path, dpi=settings.ocr_dpi)
    psm_modes = [int(x.strip()) for x in settings.ocr_psm_modes.split(",") if x.strip()] or [3]
    pages: list[PageText] = []
    for i, image in enumerate(images, start=1):
        best_text, best_conf = "", 0.0
        for variant in _image_variants(image, ImageOps, ImageFilter):
            for psm in psm_modes:
                text, conf = _tesseract(variant, settings, psm, pytesseract)
                score = conf + min(sum(1 for c in text if c.isalnum()) / 2000, 1.0) * 10
                if score > best_conf:
                    best_text, best_conf = text, conf
        pages.append(
            PageText(
                page=i,
                text=_cleanup(best_text),
                source="tesseract_ocr",
                confidence=best_conf / 100.0 if best_conf > 1 else best_conf,
            )
        )
    return pages


def _image_variants(image, ImageOps, ImageFilter):
    g = ImageOps.grayscale(image)
    a = ImageOps.autocontrast(g)
    s = a.filter(ImageFilter.SHARPEN)
    return [image, a, s]


def _tesseract(image, settings: Settings, psm: int, pytesseract) -> tuple[str, float]:
    cfg = f"--oem 1 --psm {psm}"
    text = pytesseract.image_to_string(image, lang=settings.ocr_language, config=cfg)
    data = pytesseract.image_to_data(
        image, lang=settings.ocr_language, config=cfg, output_type=pytesseract.Output.DICT
    )
    confs = [float(data["conf"][i]) for i, t in enumerate(data["text"]) if str(t).strip() and float(data["conf"][i]) >= 0]
    conf = sum(confs) / len(confs) if confs else 0.0
    return text, conf


def _cleanup(text: str) -> str:
    return text.replace("\x0c", "").replace("\r\n", "\n").replace("\r", "\n").strip("\n")
