from fastapi import APIRouter

from rag_storage.config import get_settings
from rag_storage.db import get_engine
from rag_storage.minio_client import MinioStorage
from rag_storage.qdrant_client import QdrantStore

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "rag-platform-api"}


@router.get("/health/ready")
def readiness() -> dict[str, object]:
    settings = get_settings()
    checks: dict[str, bool] = {"postgres": False, "qdrant": False, "minio": False}

    try:
        with get_engine().connect() as conn:
            from sqlalchemy import text

            conn.execute(text("SELECT 1"))
        checks["postgres"] = True
    except Exception:
        pass

    checks["qdrant"] = QdrantStore(settings).health_ok()

    try:
        MinioStorage(settings)._client.head_bucket(Bucket=settings.minio_bucket)
        checks["minio"] = True
    except Exception:
        pass

    ready = all(checks.values())
    return {"status": "ready" if ready else "degraded", "checks": checks}
