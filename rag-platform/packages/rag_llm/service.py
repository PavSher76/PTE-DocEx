from __future__ import annotations

from rag_llm.guard import (
    answer_declares_not_found,
    is_insufficient_context,
    validate_citations,
)
from rag_llm.prompts import ANSWER_WITH_CITATIONS, format_context_block
from rag_llm.providers.base import LLMProvider
from rag_llm.providers.ollama import OllamaProvider
from rag_llm.providers.openai_compat import OpenAICompatProvider
from rag_schemas.query import SearchHit
from rag_storage.config import Settings, get_settings


class QueryAnswerService:
    def __init__(self, settings: Settings | None = None):
        self._settings = settings or get_settings()
        self._providers: list[LLMProvider] = [
            OpenAICompatProvider(self._settings),
            OllamaProvider(self._settings),
        ]

    def list_models(self) -> list[str]:
        for provider in self._providers:
            models = provider.list_models()
            if models:
                return models
        return [self._settings.ollama_model]

    def answer(
        self,
        query: str,
        hits: list[SearchHit],
        *,
        model: str | None = None,
        use_llm: bool = True,
    ) -> tuple[str, list[str]]:
        """
        Возвращает (answer, warnings).
        При недоступном LLM — extractive fallback из топ-хитов.
        """
        warnings: list[str] = []

        if is_insufficient_context(hits):
            return "Не найдено в загруженных данных проекта.", warnings

        if not use_llm or not self._settings.llm_enabled:
            return self._extractive_answer(query, hits), warnings

        context = format_context_block(hits)
        prompt = ANSWER_WITH_CITATIONS.format(query=query, context=context)
        answer: str | None = None
        for provider in self._providers:
            answer = provider.generate(prompt, model=model)
            if answer:
                break

        if not answer:
            warnings.append("LLM недоступен — возвращён extractive-ответ.")
            return self._extractive_answer(query, hits), warnings

        if answer_declares_not_found(answer):
            return answer, warnings

        warnings.extend(validate_citations(answer, len(hits)))
        return answer, warnings

    def _extractive_answer(self, query: str, hits: list[SearchHit]) -> str:
        lines = [f"По запросу «{query}» найдено {len(hits)} релевантных фрагментов:\n"]
        for i, hit in enumerate(hits[:6], start=1):
            code = hit.document_code or hit.document_name or "—"
            page = hit.page_number if hit.page_number is not None else "—"
            lines.append(f"[{i}] {code}, стр. {page} ({hit.element_type}): {hit.text[:350]}…")
        lines.append(
            "\n(Подключите Ollama или OpenAI-compatible API для связного ответа с guard.)"
        )
        return "\n".join(lines)
