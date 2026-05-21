"""Цепочка парсеров: project_analysis → pte_pdf (fitz+OCR); иначе docling/unstructured/pypdf."""

from __future__ import annotations

import logging
from pathlib import Path

from rag_parsers.base import DocumentElementDTO, ParserAdapter
from rag_parsers.docling_adapter import DoclingParserAdapter
from rag_parsers.pte_pdf_adapter import PtePdfParserAdapter
from rag_parsers.pypdf_adapter import PypdfParserAdapter
from rag_parsers.unstructured_adapter import UnstructuredParserAdapter
from rag_storage.config import Settings, get_settings

logger = logging.getLogger(__name__)


def parse_document(
    path: Path,
    file_type: str,
    settings: Settings | None = None,
    *,
    rag_collection: str | None = None,
) -> tuple[list[DocumentElementDTO], str]:
    settings = settings or get_settings()
    chain = _build_chain(settings, file_type, rag_collection=rag_collection)
    errors: list[str] = []
    for parser in chain:
        try:
            elements = parser.parse(path, file_type)
            if elements:
                logger.info("Парсер %s: %s элементов из %s", parser.name, len(elements), path.name)
                return elements, parser.name
            errors.append(f"{parser.name}: нет извлекаемого текста")
            logger.warning("Parser %s: пустой результат для %s", parser.name, path.name)
        except Exception as exc:
            errors.append(f"{parser.name}: {exc}")
            logger.warning("Parser %s failed: %s", parser.name, exc)
    raise RuntimeError("Все парсеры не смогли обработать файл. " + "; ".join(errors))


def _build_chain(
    settings: Settings,
    file_type: str,
    *,
    rag_collection: str | None = None,
) -> list[ParserAdapter]:
    primary = settings.parser_primary.lower()
    fallback = settings.parser_fallback.lower()
    parsers: list[ParserAdapter] = []

    def add(name: str) -> None:
        if name == "docling":
            parsers.append(DoclingParserAdapter())
        elif name == "unstructured":
            parsers.append(UnstructuredParserAdapter())
        elif name == "pypdf":
            parsers.append(PypdfParserAdapter())
        elif name == "pte_pdf":
            parsers.append(PtePdfParserAdapter(settings))

    # «Анализ проекта»: тот же базовый пайплайн, что и контроль переписки (fitz → OCR).
    if file_type == "pdf" and (rag_collection or "").strip() == "project_analysis":
        logger.info("Цепочка парсеров: pte_pdf (fitz+OCR) для rag_collection=project_analysis")
        return [PtePdfParserAdapter(settings)]

    # Документы ИСМ: office-форматы через unstructured/docling, PDF — pypdf/docling.
    if (rag_collection or "").strip() == "ism":
        if file_type == "pdf":
            if primary != "pypdf":
                add(primary)
            add("pypdf")
        else:
            if primary not in ("pypdf", "pte_pdf"):
                add(primary)
            if fallback not in (primary, "pypdf", "pte_pdf"):
                add(fallback)
        return parsers or [UnstructuredParserAdapter()]

    if file_type == "pdf":
        if primary != "pypdf":
            add(primary)
        if fallback not in (primary, "pypdf"):
            add(fallback)
        if not any(p.name == "pypdf" for p in parsers):
            parsers.append(PypdfParserAdapter())
        return parsers

    add(primary)
    if fallback != primary:
        add(fallback)
    return parsers
