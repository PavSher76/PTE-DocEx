"""Базовое извлечение текста из PDF (как PTE-DocEx: переписка / document_text).

1. Текстовый слой PyMuPDF (fitz), sort=True
2. При нехватке символов — Tesseract OCR (pdf2image + poppler)
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from rag_parsers.base import DocumentElementDTO
from rag_storage.config import Settings


@dataclass(frozen=True)
class _PageText:
    page: int
    text: str
    source: str


def extract_pdf_elements(path: Path, settings: Settings) -> list[DocumentElementDTO]:
    pages = _extract_with_fitz(path)
    if not _has_enough_text(pages, settings):
        pages = _extract_ocr_pages(path, settings)

    elements: list[DocumentElementDTO] = []
    for page in pages:
        text = page.text.strip()
        if not text:
            continue
        elements.append(
            DocumentElementDTO(
                page_number=page.page,
                element_type="text",
                text=text,
                reading_order=page.page,
                metadata={
                    "parser": "pte_pdf",
                    "source": page.source,
                    "ocr_risk": page.source.startswith("tesseract"),
                },
            )
        )
    return elements


def _extract_with_fitz(pdf_path: Path) -> list[_PageText]:
    try:
        import fitz
    except ImportError as exc:
        raise RuntimeError(
            "PyMuPDF не установлен: pip install pymupdf"
        ) from exc

    try:
        document = fitz.open(pdf_path)
    except Exception as exc:
        raise RuntimeError(f"PyMuPDF не смог открыть PDF: {pdf_path.name}") from exc

    pages: list[_PageText] = []
    try:
        for index, page in enumerate(document, start=1):
            text = page.get_text("text", sort=True)
            pages.append(
                _PageText(
                    page=index,
                    text=_cleanup_text(text),
                    source="pymupdf_text_layer",
                )
            )
    finally:
        document.close()
    return pages


def _extract_ocr_pages(pdf_path: Path, settings: Settings) -> list[_PageText]:
    try:
        import pytesseract
        from pdf2image import convert_from_path
        from PIL import Image, ImageFilter, ImageOps
    except ImportError as exc:
        raise RuntimeError(
            "OCR недоступен: pip install pytesseract pdf2image Pillow "
            "и установите tesseract-ocr + poppler-utils в системе"
        ) from exc

    try:
        images = convert_from_path(pdf_path, dpi=settings.ocr_dpi)
    except Exception as exc:
        raise RuntimeError(f"Не удалось прочитать PDF для OCR: {pdf_path.name}") from exc

    psm_modes = _parse_psm_modes(settings.ocr_psm_modes)
    pages: list[_PageText] = []
    for index, image in enumerate(images, start=1):
        candidates = [
            _run_tesseract(candidate, settings, psm, pytesseract, ImageOps, ImageFilter)
            for candidate in _image_candidates(image, ImageOps, ImageFilter)
            for psm in psm_modes
        ]
        best_text, best_confidence = max(candidates, key=lambda item: _candidate_score(item[0], item[1]))
        if not best_text.strip():
            raise RuntimeError(f"Tesseract не смог распознать страницу {index} PDF: {pdf_path.name}")
        pages.append(
            _PageText(
                page=index,
                text=_cleanup_text(best_text),
                source="tesseract_ocr",
            )
        )
    return pages


def _has_enough_text(pages: list[_PageText], settings: Settings) -> bool:
    total_chars = sum(len(page.text.strip()) for page in pages)
    return total_chars >= settings.ocr_min_text_layer_chars


def _image_candidates(image, ImageOps, ImageFilter) -> list:
    grayscale = ImageOps.grayscale(image)
    autocontrast = ImageOps.autocontrast(grayscale)
    sharpened = autocontrast.filter(ImageFilter.SHARPEN)
    thresholded = sharpened.point(lambda pixel: 255 if pixel > 180 else 0)
    return [image, autocontrast, sharpened, thresholded]


def _run_tesseract(image, settings: Settings, psm: int, pytesseract, ImageOps, ImageFilter) -> tuple[str, float]:
    config = f"--oem 1 --psm {psm}"
    try:
        text = pytesseract.image_to_string(image, lang=settings.ocr_language, config=config)
        data = pytesseract.image_to_data(
            image,
            lang=settings.ocr_language,
            config=config,
            output_type=pytesseract.Output.DICT,
        )
    except Exception as exc:
        raise RuntimeError("Tesseract не смог выполнить OCR.") from exc

    confidences: list[float] = []
    for index, raw_text in enumerate(data.get("text", [])):
        if not str(raw_text).strip():
            continue
        confidence = _parse_confidence(data.get("conf", ["-1"])[index])
        if confidence >= 0:
            confidences.append(confidence)

    confidence = sum(confidences) / len(confidences) if confidences else 0.0
    return text, confidence


def _candidate_score(text: str, confidence: float) -> float:
    recognized_chars = sum(1 for char in text if char.isalnum())
    recognized_bonus = min(recognized_chars / 2000, 1.0) * 10
    return confidence + recognized_bonus


def _parse_confidence(value: object) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return -1.0


def _parse_psm_modes(raw_value: str) -> list[int]:
    modes: list[int] = []
    for item in raw_value.split(","):
        try:
            mode = int(item.strip())
        except ValueError:
            continue
        if mode not in modes:
            modes.append(mode)
    return modes or [3]


def _cleanup_text(text: str) -> str:
    return text.replace("\x0c", "").replace("\r\n", "\n").replace("\r", "\n").strip("\n")
