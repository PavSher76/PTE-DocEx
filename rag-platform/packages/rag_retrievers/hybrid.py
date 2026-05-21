"""Hybrid retrieval: dense + sparse + RRF fusion + rerank."""

from __future__ import annotations

from uuid import UUID

from qdrant_client.http import models as qmodels

from rag_embeddings.dense import DenseEmbedder
from rag_embeddings.sparse import SparseEmbedder
from rag_retrievers.rerank import rerank_hits
from rag_schemas.query import SearchFilters, SearchHit
from rag_storage.config import Settings
from rag_storage.qdrant_client import QdrantStore


class HybridRetriever:
    def __init__(self, settings: Settings | None = None):
        from rag_storage.config import get_settings

        self._settings = settings or get_settings()
        self._qdrant = QdrantStore(self._settings)
        self._dense = DenseEmbedder(self._settings)
        self._sparse = SparseEmbedder()
        self._qdrant.ensure_collections(self._dense.dimension)

    def search(
        self,
        *,
        project_id: str,
        query: str,
        filters: SearchFilters,
        top_k: int = 10,
        collection: str | None = None,
        use_hybrid: bool | None = None,
        rerank: bool | None = None,
    ) -> list[SearchHit]:
        collection_name = collection or self._settings.qdrant_collection_text
        hybrid = self._settings.hybrid_search_enabled if use_hybrid is None else use_hybrid
        do_rerank = self._settings.rerank_enabled if rerank is None else rerank

        dense_vector = self._dense.embed(query)
        sparse_indices, sparse_values = self._sparse.embed(query)
        query_filter = self._build_filter(project_id, filters)

        if hybrid and sparse_indices:
            response = self._qdrant.hybrid_search(
                collection_name,
                dense_vector=dense_vector,
                sparse_indices=sparse_indices,
                sparse_values=sparse_values,
                query_filter=query_filter,
                limit=top_k,
            )
        else:
            response = self._qdrant.client.query_points(
                collection_name=collection_name,
                query=dense_vector,
                query_filter=query_filter,
                limit=top_k,
                with_payload=True,
            )

        hits = [self._to_hit(point) for point in response.points]
        if do_rerank:
            hits = rerank_hits(query, hits, top_k=top_k)
        return hits

    def search_by_requirement(
        self,
        *,
        project_id: str,
        query: str,
        filters: SearchFilters,
        top_k: int = 10,
    ) -> list[SearchHit]:
        filters = filters.model_copy(update={"element_type": "requirement"})
        return self.search(project_id=project_id, query=query, filters=filters, top_k=top_k)

    def search_by_ntd(
        self,
        *,
        project_id: str,
        ntd_ref: str,
        filters: SearchFilters,
        top_k: int = 10,
    ) -> list[SearchHit]:
        """Поиск токенов, в payload которых есть ссылка на НТД."""
        collection_name = self._settings.qdrant_collection_text
        query_filter = self._build_filter(project_id, filters)
        query_filter.must.append(
            qmodels.FieldCondition(
                key="ntd_refs",
                match=qmodels.MatchAny(any=[ntd_ref]),
            )
        )
        dense_vector = self._dense.embed(ntd_ref)
        response = self._qdrant.client.query_points(
            collection_name=collection_name,
            query=dense_vector,
            query_filter=query_filter,
            limit=top_k,
            with_payload=True,
        )
        return [self._to_hit(point) for point in response.points]

    def _build_filter(self, project_id: str, filters: SearchFilters) -> qmodels.Filter:
        must: list[qmodels.FieldCondition] = [
            qmodels.FieldCondition(key="project_id", match=qmodels.MatchValue(value=project_id)),
        ]
        if filters.stage:
            must.append(
                qmodels.FieldCondition(key="stage", match=qmodels.MatchValue(value=filters.stage.value))
            )
        if filters.discipline:
            must.append(
                qmodels.FieldCondition(key="discipline", match=qmodels.MatchValue(value=filters.discipline))
            )
        if filters.document_code:
            must.append(
                qmodels.FieldCondition(
                    key="document_code", match=qmodels.MatchValue(value=filters.document_code)
                )
            )
        if filters.revision:
            must.append(
                qmodels.FieldCondition(key="revision", match=qmodels.MatchValue(value=filters.revision))
            )
        if filters.element_type:
            must.append(
                qmodels.FieldCondition(
                    key="element_type", match=qmodels.MatchValue(value=filters.element_type)
                )
            )
        if filters.page_number is not None:
            must.append(
                qmodels.FieldCondition(
                    key="page_number", match=qmodels.MatchValue(value=filters.page_number)
                )
            )
        if filters.status:
            must.append(
                qmodels.FieldCondition(key="status", match=qmodels.MatchValue(value=filters.status))
            )
        return qmodels.Filter(must=must)

    def _to_hit(self, point: object) -> SearchHit:
        payload = getattr(point, "payload", None) or {}
        return SearchHit(
            token_id=UUID(str(getattr(point, "id"))),
            score=float(getattr(point, "score", None) or 0),
            text=str(payload.get("text", "")),
            document_id=UUID(str(payload.get("document_id"))),
            document_name=payload.get("document_name"),
            document_code=payload.get("document_code"),
            page_number=payload.get("page_number"),
            sheet_number=payload.get("sheet_number"),
            element_type=str(payload.get("element_type", "text")),
            bbox=payload.get("bbox"),
            source_uri=str(payload.get("source_uri", "")),
            metadata={
                "ntd_refs": payload.get("ntd_refs", []),
                "revision": payload.get("revision"),
                "status": payload.get("status"),
                "section_path": payload.get("section_path", []),
                **(payload.get("metadata") or {}),
            },
        )
