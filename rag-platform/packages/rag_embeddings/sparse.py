"""Sparse-векторы (BM25-подобная схема) для hybrid search в Qdrant."""

from __future__ import annotations

import math
import re
from collections import Counter

TOKEN_RE = re.compile(r"[\w\u0400-\u04FF]+", re.UNICODE)


class SparseEmbedder:
    """Лёгкий sparse embedder без внешних моделей (Sprint 2)."""

    def __init__(self, *, vocab_size: int = 2**18) -> None:
        self._vocab_size = vocab_size

    def embed(self, text: str) -> tuple[list[int], list[float]]:
        tokens = [t.lower() for t in TOKEN_RE.findall(text) if len(t) > 1]
        if not tokens:
            return [], []
        counts = Counter(tokens)
        length = len(tokens)
        weighted: dict[int, float] = {}
        for token, count in counts.items():
            index = hash(token) % self._vocab_size
            tf = 1.0 + math.log(count)
            idf_like = 1.0 + math.log(1.0 + length / count)
            weight = tf * idf_like
            weighted[index] = weighted.get(index, 0.0) + weight
        indices = list(weighted.keys())
        values = [float(v) for v in weighted.values()]
        return indices, values

    def embed_batch(self, texts: list[str]) -> list[tuple[list[int], list[float]]]:
        return [self.embed(text) for text in texts]
