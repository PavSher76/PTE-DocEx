from pathlib import Path

import fitz
from pydantic import BaseModel

from app.config import Settings
from app.services.ocr import ExtractedPage, extract_pdf_pages


class PdfTextResult(BaseModel):
    text: str
    pages: list[str]


def extract_pdf_text(pdf_path: Path, settings: Settings) -> PdfTextResult:
    if pdf_path.suffix.lower() != ".pdf":
        raise ValueError("Файл исходящей переписки должен быть PDF.")

    extracted_pages = _extract_letter_text_with_fitz(pdf_path, settings)
    if not _has_enough_text(extracted_pages, settings):
        extracted_pages = extract_pdf_pages(pdf_path, settings, use_text_layer=False)
    pages = [page.text for page in extracted_pages]

    text = "\n\n".join(page for page in pages if page)
    if not text.strip():
        raise ValueError("OCR не извлек текст из PDF. Проверьте качество скана или язык OCR.")

    return PdfTextResult(text=text, pages=pages)


def _extract_letter_text_with_fitz(pdf_path: Path, settings: Settings) -> list[ExtractedPage]:
    try:
        document = fitz.open(pdf_path)
    except Exception as exc:
        raise RuntimeError(f"PyMuPDF не смог открыть PDF письма: {pdf_path.name}") from exc

    pages: list[ExtractedPage] = []
    try:
        for index, page in enumerate(document, start=1):
            text = page.get_text("text", sort=True)
            pages.append(
                ExtractedPage(
                    page=index,
                    text=_cleanup_fitz_text(text),
                    confidence=100.0 if text.strip() else 0.0,
                    source="pymupdf_text_layer",
                )
            )
    finally:
        document.close()

    return pages


def _has_enough_text(pages: list[ExtractedPage], settings: Settings) -> bool:
    total_chars = sum(len(page.text.strip()) for page in pages)
    return total_chars >= settings.ocr_min_text_layer_chars


def _cleanup_fitz_text(text: str) -> str:
    return text.replace("\x0c", "").replace("\r\n", "\n").replace("\r", "\n").strip("\n")
