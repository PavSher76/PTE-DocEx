from fastapi import APIRouter

from rag_llm.service import QueryAnswerService
from rag_retrievers.hybrid import HybridRetriever
from rag_schemas.query import NtdSearchRequest, QueryRequest, QueryResponse, SearchRequest
from rag_storage.config import get_settings

router = APIRouter()


@router.post("/search")
def search(body: SearchRequest) -> dict:
    retriever = HybridRetriever()
    hits = retriever.search(
        project_id=body.project_id,
        query=body.query,
        filters=body.filters,
        top_k=body.top_k,
        use_hybrid=True,
    )
    return {"hits": hits, "total": len(hits), "mode": "hybrid"}


@router.post("/search/hybrid")
def search_hybrid(body: SearchRequest) -> dict:
    retriever = HybridRetriever()
    hits = retriever.search(
        project_id=body.project_id,
        query=body.query,
        filters=body.filters,
        top_k=body.top_k,
        use_hybrid=True,
        rerank=True,
    )
    return {
        "hits": hits,
        "total": len(hits),
        "mode": "hybrid+rerank",
        "debug": _debug_payload(body, hits) if body.debug else None,
    }


@router.post("/search/by-requirement")
def search_by_requirement(body: SearchRequest) -> dict:
    hits = HybridRetriever().search_by_requirement(
        project_id=body.project_id,
        query=body.query,
        filters=body.filters,
        top_k=body.top_k,
    )
    return {"hits": hits, "total": len(hits), "mode": "requirement"}


@router.post("/search/project-analysis")
def search_project_analysis(body: SearchRequest) -> dict:
    """Поиск по коллекции «Анализ проекта»."""
    settings = get_settings()
    hits = HybridRetriever(settings).search(
        project_id=body.project_id,
        query=body.query,
        filters=body.filters,
        top_k=body.top_k,
        collection=settings.qdrant_collection_project_analysis,
        use_hybrid=True,
        rerank=True,
    )
    return {
        "hits": hits,
        "total": len(hits),
        "collection": settings.qdrant_collection_project_analysis,
        "collection_label": "Анализ проекта",
        "debug": _debug_payload(body, hits) if body.debug else None,
    }


@router.post("/search/drawings")
def search_drawings(body: SearchRequest) -> dict:
    settings = get_settings()
    hits = HybridRetriever(settings).search(
        project_id=body.project_id,
        query=body.query,
        filters=body.filters,
        top_k=body.top_k,
        collection=settings.qdrant_collection_drawings_text,
        use_hybrid=True,
        rerank=True,
    )
    return {
        "hits": hits,
        "total": len(hits),
        "collection": settings.qdrant_collection_drawings_text,
        "debug": _debug_payload(body, hits) if body.debug else None,
    }


@router.post("/search/by-ntd")
def search_by_ntd(body: NtdSearchRequest) -> dict:
    hits = HybridRetriever().search_by_ntd(
        project_id=body.project_id,
        ntd_ref=body.ntd_ref,
        filters=body.filters,
        top_k=body.top_k,
    )
    return {"hits": hits, "total": len(hits), "mode": "ntd", "ntd_ref": body.ntd_ref}


@router.post("/query", response_model=QueryResponse)
def query(body: QueryRequest) -> QueryResponse:
    retriever = HybridRetriever()
    hits = retriever.search(
        project_id=body.project_id,
        query=body.query,
        filters=body.filters,
        top_k=body.top_k,
        use_hybrid=True,
        rerank=True,
    )
    if not hits:
        return QueryResponse(
            answer="Не найдено в загруженных данных проекта.",
            hits=[],
            citations=[],
            debug_chunks=[] if body.debug else None,
            llm_used=False,
        )

    llm_service = QueryAnswerService()
    answer, warnings = llm_service.answer(
        body.query,
        hits[:8],
        model=body.model,
        use_llm=body.use_llm,
    )
    llm_used = body.use_llm and get_settings().llm_enabled and not any(
        "extractive" in w.lower() or "недоступен" in w.lower() for w in warnings
    )
    return QueryResponse(
        answer=answer,
        hits=hits,
        citations=hits[:8],
        debug_chunks=hits if body.debug else None,
        llm_used=llm_used,
        warnings=warnings,
    )


def _debug_payload(body: SearchRequest, hits: list) -> dict:
    return {
        "query": body.query,
        "filters": body.filters.model_dump(),
        "retrieved": [
            {
                "token_id": str(h.token_id),
                "score": h.score,
                "element_type": h.element_type,
                "page": h.page_number,
                "text_preview": h.text[:200],
            }
            for h in hits
        ],
    }
