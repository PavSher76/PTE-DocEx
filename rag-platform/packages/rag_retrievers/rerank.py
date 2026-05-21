"""Лёгкий reranker поверх fusion-скоров (Sprint 2)."""

from __future__ import annotations

import re

from rag_schemas.query import SearchHit

REQUIREMENT_HINT = re.compile(
    r"\b(должен|необходимо|требу|исходн|данн|раздел)\b", re.IGNORECASE
)
NTD_HINT = re.compile(r"\b(СП|ГОСТ|СанПиН|ФНП)\b", re.IGNORECASE)


def rerank_hits(query: str, hits: list[SearchHit], *, top_k: int) -> list[SearchHit]:
    if not hits:
        return []
    query_lower = query.lower()
    wants_requirement = bool(REQUIREMENT_HINT.search(query))
    wants_ntd = bool(NTD_HINT.search(query))

    scored: list[tuple[float, SearchHit]] = []
    for hit in hits:
        bonus = 0.0
        text_lower = hit.text.lower()
        if wants_requirement and hit.element_type == "requirement":
            bonus += 0.15
        if wants_ntd and hit.metadata.get("ntd_refs"):
            bonus += 0.12
        if query_lower[:24] in text_lower:
            bonus += 0.08
        if hit.document_code and hit.document_code.lower() in query_lower:
            bonus += 0.1
        scored.append((hit.score + bonus, hit))

    scored.sort(key=lambda item: item[0], reverse=True)
    result: list[SearchHit] = []
    for score, hit in scored[:top_k]:
        result.append(hit.model_copy(update={"score": round(score, 6)}))
    return result
