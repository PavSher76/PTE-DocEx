"""Парсер PDF для «Анализ проекта»: PyMuPDF + OCR (как контроль переписки PTE-DocEx)."""

from __future__ import annotations

from pathlib import Path

from rag_parsers.base import DocumentElementDTO, ParserAdapter
from rag_parsers.pdf_extract import extract_pdf_elements
from rag_storage.config import Settings


class PtePdfParserAdapter(ParserAdapter):
    name = "pte_pdf"

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def parse(self, path: Path, file_type: str) -> list[DocumentElementDTO]:
        if file_type != "pdf":
            raise ValueError("pte_pdf поддерживает только PDF")
        elements = extract_pdf_elements(path, self._settings)
        if not elements:
            raise RuntimeError(
                "pte_pdf: нет текста (ни текстовый слой PyMuPDF, ни OCR Tesseract). "
                "Проверьте качество скана и tesseract-ocr-rus."
            )
        return elements
