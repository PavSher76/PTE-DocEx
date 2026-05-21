"""Dense-эмбеддинги: sentence-transformers при наличии, иначе детерминированный fallback."""

from __future__ import annotations

import hashlib
import struct
from functools import lru_cache

from rag_storage.config import Settings


class DenseEmbedder:
    def __init__(self, settings: Settings | None = None):
        from rag_storage.config import get_settings

        self._settings = settings or get_settings()
        self._dimension = self._settings.embedding_dimension
        self._model = None
        self._backend = "hash"
        if self._settings.embedding_use_sentence_transformers:
            self._model = _load_sentence_transformer(self._settings.embedding_model)
            if self._model is not None:
                self._backend = "sentence-transformers"
                self._dimension = int(self._model.get_sentence_embedding_dimension())

    @property
    def dimension(self) -> int:
        return self._dimension

    @property
    def backend(self) -> str:
        return self._backend

    def embed(self, text: str) -> list[float]:
        if self._model is not None:
            vector = self._model.encode(text, normalize_embeddings=True)
            return vector.tolist()
        return self._hash_embed(text)

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        if self._model is not None:
            vectors = self._model.encode(texts, normalize_embeddings=True)
            return [row.tolist() for row in vectors]
        return [self._hash_embed(text) for text in texts]

    def _hash_embed(self, text: str) -> list[float]:
        digest = hashlib.sha256(text.encode("utf-8")).digest()
        values: list[float] = []
        while len(values) < self._dimension:
            for chunk_start in range(0, len(digest), 4):
                if len(values) >= self._dimension:
                    break
                chunk = digest[chunk_start : chunk_start + 4]
                if len(chunk) < 4:
                    chunk = chunk.ljust(4, b"\0")
                num = struct.unpack("!I", chunk)[0]
                values.append((num / 2**32) * 2 - 1)
            digest = hashlib.sha256(digest).digest()
        return values[: self._dimension]


@lru_cache(maxsize=1)
def _load_sentence_transformer(model_name: str):
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError:
        return None
    try:
        return SentenceTransformer(model_name)
    except Exception:
        return None
