from fastapi import APIRouter

from rag_llm.service import QueryAnswerService
from rag_storage.config import get_settings

router = APIRouter(prefix="/llm", tags=["llm"])


@router.get("/models")
def list_llm_models() -> dict:
    settings = get_settings()
    service = QueryAnswerService(settings)
    return {"models": service.list_models(), "default": settings.ollama_model}
