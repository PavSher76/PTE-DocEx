"""Индексация векторов ИСМ в отдельные коллекции Qdrant."""

from __future__ import annotations

from typing import Any, Literal
from uuid import UUID

from fastapi import APIRouter
from pydantic import BaseModel, Field

from rag_embeddings.dense import DenseEmbedder
from rag_embeddings.sparse import SparseEmbedder
from rag_storage.config import get_settings
from rag_storage.qdrant_client import QdrantStore

router = APIRouter(prefix="/ism/vectors", tags=["ism-vectors"])

IsmVectorCollection = Literal["documents", "requirements", "interfaces"]


class IsmVectorItem(BaseModel):
    point_id: str
    collection: IsmVectorCollection
    text: str = Field(min_length=1)
    payload: dict[str, Any] = Field(default_factory=dict)


class IsmIndexRequest(BaseModel):
    project_id: str
    document_id: str
    items: list[IsmVectorItem] = Field(default_factory=list)
    delete_document_first: bool = True


class IsmIndexResponse(BaseModel):
    indexed: int
    collections: dict[str, int]


_COLLECTION_MAP = {
    "documents": lambda s: s.qdrant_collection_ism_documents,
    "requirements": lambda s: s.qdrant_collection_ism_requirements,
    "interfaces": lambda s: s.qdrant_collection_ism_interfaces,
}


@router.post("/index", response_model=IsmIndexResponse)
def index_ism_vectors(body: IsmIndexRequest) -> IsmIndexResponse:
    settings = get_settings()
    dense = DenseEmbedder(settings)
    sparse = SparseEmbedder()
    qdrant = QdrantStore(settings)
    qdrant.ensure_collections(dense.dimension)

    if body.delete_document_first:
        for name_fn in _COLLECTION_MAP.values():
            try:
                qdrant.delete_by_document_id(name_fn(settings), UUID(body.document_id))
            except Exception:
                pass

    counts: dict[str, int] = {"documents": 0, "requirements": 0, "interfaces": 0}
    for item in body.items:
        coll_name = _COLLECTION_MAP[item.collection](settings)
        dense_vector = dense.embed(item.text)
        sparse_indices, sparse_values = sparse.embed(item.text)
        payload = {
            **item.payload,
            "project_id": body.project_id,
            "document_id": body.document_id,
            "text": item.text[:4000],
        }
        qdrant.upsert_token(
            coll_name,
            token_id=UUID(item.point_id),
            dense_vector=dense_vector,
            sparse_indices=sparse_indices,
            sparse_values=sparse_values,
            payload=payload,
        )
        counts[item.collection] += 1

    return IsmIndexResponse(indexed=sum(counts.values()), collections=counts)
