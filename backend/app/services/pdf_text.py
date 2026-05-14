from pathlib import Path

from pydantic import BaseModel

from app.config import Settings
from app.services.ocr import extract_pdf_pages


class PdfTextResult(BaseModel):
    text: str
    pages: list[str]


def extract_pdf_text(pdf_path: Path, settings: Settings) -> PdfTextResult:
    if pdf_path.suffix.lower() != ".pdf":
        raise ValueError("Файл исходящей переписки должен быть PDF.")

    extracted_pages = extract_pdf_pages(pdf_path, settings)
    pages = [page.text for page in extracted_pages]

    text = "\n\n".join(page for page in pages if page)
    if not text.strip():
        raise ValueError("OCR не извлек текст из PDF. Проверьте качество скана или язык OCR.")

    return PdfTextResult(text=text, pages=pages)
