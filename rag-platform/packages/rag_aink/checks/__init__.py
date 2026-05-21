"""Регистрация всех проверок AI-NK при импорте пакета."""

from rag_aink.checks import (
    document_set,
    interdisciplinary,
    ntd_refs,
    requirements_trace,
    source_data,
    stamps,
    title_blocks,
)

__all__ = [
    "document_set",
    "interdisciplinary",
    "ntd_refs",
    "requirements_trace",
    "source_data",
    "stamps",
    "title_blocks",
]
