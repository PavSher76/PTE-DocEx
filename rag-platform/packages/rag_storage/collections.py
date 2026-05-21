"""Имена коллекций Qdrant и выбор по назначению документа."""

from __future__ import annotations

from rag_storage.config import Settings
from rag_storage.models import Document

# Значение documents.rag_collection для раздела «Анализ проекта» (PTE-DocEx)
RAG_COLLECTION_PROJECT_ANALYSIS = "project_analysis"
RAG_COLLECTION_ISM = "ism"

COLLECTION_LABELS = {
    RAG_COLLECTION_PROJECT_ANALYSIS: "Анализ проекта",
    RAG_COLLECTION_ISM: "Документы ИСМ",
}


def text_collection_for(document: Document, settings: Settings) -> str:
    if document.rag_collection == RAG_COLLECTION_PROJECT_ANALYSIS:
        return settings.qdrant_collection_project_analysis
    if document.rag_collection == RAG_COLLECTION_ISM:
        return settings.qdrant_collection_ism_documents
    return settings.qdrant_collection_text


def ism_requirements_collection(settings: Settings) -> str:
    return settings.qdrant_collection_ism_requirements


def ism_interfaces_collection(settings: Settings) -> str:
    return settings.qdrant_collection_ism_interfaces


def drawings_collection_for(document: Document, settings: Settings) -> str:
    if document.rag_collection == RAG_COLLECTION_PROJECT_ANALYSIS:
        return settings.qdrant_collection_project_analysis_drawings
    return settings.qdrant_collection_drawings_text


def all_collection_names(settings: Settings) -> list[str]:
    return [
        settings.qdrant_collection_text,
        settings.qdrant_collection_drawings_text,
        settings.qdrant_collection_project_analysis,
        settings.qdrant_collection_project_analysis_drawings,
        settings.qdrant_collection_ism_documents,
        settings.qdrant_collection_ism_requirements,
        settings.qdrant_collection_ism_interfaces,
        "project_drawings_visual",
        "project_requirements",
        "normative_documents",
    ]
