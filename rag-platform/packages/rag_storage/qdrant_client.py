from typing import Any
from uuid import UUID

from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels

from rag_storage.config import Settings
from rag_storage.collections import all_collection_names


class QdrantStore:
    def __init__(self, settings: Settings):
        self._settings = settings
        self._client = QdrantClient(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key or None,
        )

    @property
    def client(self) -> QdrantClient:
        return self._client

    def ensure_collections(self, vector_size: int | None = None) -> None:
        dim = vector_size or self._settings.embedding_dimension
        for name in all_collection_names(self._settings):
            if self._client.collection_exists(name):
                self._recreate_if_missing_sparse(name)
                continue
            self._client.create_collection(
                collection_name=name,
                vectors_config=qmodels.VectorParams(size=dim, distance=qmodels.Distance.COSINE),
                sparse_vectors_config={
                    "sparse": qmodels.SparseVectorParams(
                        index=qmodels.SparseIndexParams(on_disk=False)
                    )
                },
            )

    def _recreate_if_missing_sparse(self, name: str) -> None:
        info = self._client.get_collection(name)
        vectors = info.config.params.vectors
        if isinstance(vectors, dict) and "sparse" not in (info.config.params.sparse_vectors or {}):
            return

    def upsert_token(
        self,
        collection: str,
        *,
        token_id: UUID,
        dense_vector: list[float],
        sparse_indices: list[int] | None = None,
        sparse_values: list[float] | None = None,
        payload: dict[str, Any],
    ) -> None:
        vector: dict[str, Any] = {"": dense_vector}
        if sparse_indices and sparse_values:
            vector["sparse"] = qmodels.SparseVector(indices=sparse_indices, values=sparse_values)
        self._client.upsert(
            collection_name=collection,
            points=[
                qmodels.PointStruct(
                    id=str(token_id),
                    vector=vector,
                    payload=payload,
                )
            ],
        )

    def hybrid_search(
        self,
        collection: str,
        *,
        dense_vector: list[float],
        sparse_indices: list[int],
        sparse_values: list[float],
        query_filter: qmodels.Filter | None,
        limit: int,
    ):
        if sparse_indices and sparse_values:
            return self._client.query_points(
                collection_name=collection,
                prefetch=[
                    qmodels.Prefetch(
                        query=dense_vector,
                        using="",
                        limit=max(limit * 3, 20),
                        filter=query_filter,
                    ),
                    qmodels.Prefetch(
                        query=qmodels.SparseVector(indices=sparse_indices, values=sparse_values),
                        using="sparse",
                        limit=max(limit * 3, 20),
                        filter=query_filter,
                    ),
                ],
                query=qmodels.FusionQuery(fusion=qmodels.Fusion.RRF),
                limit=limit,
                with_payload=True,
            )
        return self._client.query_points(
            collection_name=collection,
            query=dense_vector,
            query_filter=query_filter,
            limit=limit,
            with_payload=True,
        )

    def delete_by_document_version(self, collection: str, version_id: UUID) -> None:
        self._client.delete(
            collection_name=collection,
            points_selector=qmodels.FilterSelector(
                filter=qmodels.Filter(
                    must=[
                        qmodels.FieldCondition(
                            key="version_id",
                            match=qmodels.MatchValue(value=str(version_id)),
                        )
                    ]
                )
            ),
        )

    def delete_by_document_id(self, collection: str, document_id: UUID) -> None:
        self._client.delete(
            collection_name=collection,
            points_selector=qmodels.FilterSelector(
                filter=qmodels.Filter(
                    must=[
                        qmodels.FieldCondition(
                            key="document_id",
                            match=qmodels.MatchValue(value=str(document_id)),
                        )
                    ]
                )
            ),
        )

    def health_ok(self) -> bool:
        try:
            self._client.get_collections()
            return True
        except Exception:
            return False
