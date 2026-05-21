"""Проверки faithfulness: ответ только из контекста."""

from __future__ import annotations

import re

from rag_schemas.query import SearchHit

_NOT_FOUND_PHRASES = (
    "не найдено в загруженных данных",
    "нет данных в загруженных",
    "информация отсутствует в контексте",
)

_CITATION_RE = re.compile(r"\[(\d+)\]")


def is_insufficient_context(hits: list[SearchHit], min_score: float = 0.15) -> bool:
    if not hits:
        return True
    return max(h.score for h in hits) < min_score


def answer_declares_not_found(answer: str) -> bool:
    lower = answer.lower()
    return any(p in lower for p in _NOT_FOUND_PHRASES)


def citation_indices(answer: str) -> set[int]:
    return {int(m.group(1)) for m in _CITATION_RE.finditer(answer)}


def validate_citations(answer: str, hit_count: int) -> list[str]:
    """Возвращает список предупреждений о некорректных ссылках [N]."""
    warnings: list[str] = []
    for idx in citation_indices(answer):
        if idx < 1 or idx > hit_count:
            warnings.append(f"Ссылка [{idx}] вне диапазона 1..{hit_count}")
    return warnings
