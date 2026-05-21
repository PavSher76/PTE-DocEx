"""Маршрутизация парсера «Анализ проекта»."""

from rag_parsers.factory import _build_chain
from rag_storage.config import Settings


def test_project_analysis_uses_pte_pdf_parser() -> None:
    settings = Settings()
    chain = _build_chain(settings, "pdf", rag_collection="project_analysis")
    assert len(chain) == 1
    assert chain[0].name == "pte_pdf"


def test_default_pdf_uses_pypdf_in_chain() -> None:
    settings = Settings(parser_primary="pypdf", parser_fallback="pypdf")
    chain = _build_chain(settings, "pdf", rag_collection=None)
    assert any(p.name == "pypdf" for p in chain)
