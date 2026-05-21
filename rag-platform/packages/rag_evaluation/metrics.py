"""Метрики retrieval и faithfulness (этап 13)."""

from __future__ import annotations

from dataclasses import dataclass

from rag_schemas.query import SearchHit


@dataclass
class RetrievalMetrics:
    precision_at_k: float
    recall_at_k: float
    hit_count: int
    expected_count: int


def precision_at_k(
    retrieved_token_ids: list[str],
    expected_token_ids: list[str],
    k: int,
) -> float:
    if k <= 0:
        return 0.0
    top = retrieved_token_ids[:k]
    if not top:
        return 0.0
    expected = set(expected_token_ids)
    hits = sum(1 for tid in top if tid in expected)
    return hits / len(top)


def recall_at_k(
    retrieved_token_ids: list[str],
    expected_token_ids: list[str],
    k: int,
) -> float:
    expected = set(expected_token_ids)
    if not expected:
        return 1.0
    top = set(retrieved_token_ids[:k])
    return len(top & expected) / len(expected)


def compute_retrieval_metrics(
    hits: list[SearchHit],
    expected_token_ids: list[str],
    k: int = 5,
) -> RetrievalMetrics:
    retrieved = [str(h.token_id) for h in hits]
    return RetrievalMetrics(
        precision_at_k=precision_at_k(retrieved, expected_token_ids, k),
        recall_at_k=recall_at_k(retrieved, expected_token_ids, k),
        hit_count=len(hits),
        expected_count=len(expected_token_ids),
    )


def citation_correctness(answer: str, hit_count: int) -> float:
    """Доля корректных ссылок [N] в ответе (1.0 если ссылок нет)."""
    import re

    refs = [int(m.group(1)) for m in re.finditer(r"\[(\d+)\]", answer)]
    if not refs:
        return 1.0
    valid = sum(1 for n in refs if 1 <= n <= hit_count)
    return valid / len(refs)


def answer_faithfulness_score(
    answer: str,
    *,
    declares_not_found: bool,
    context_empty: bool,
) -> float:
    """
    Эвристика 0..1: 1 если ответ согласован с отсутствием/наличием контекста.
    """
    lower = answer.lower()
    not_found = "не найдено в загруженных данных" in lower
    if context_empty:
        return 1.0 if not_found or declares_not_found else 0.0
    return 0.0 if not_found else 1.0
