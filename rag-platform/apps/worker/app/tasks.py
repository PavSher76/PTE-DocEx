from uuid import UUID

from rag_storage.config import get_settings
from rag_storage.db import get_session_factory
from app.pipeline import process_job


def process_document_version(job_id: str) -> str:
    settings = get_settings()
    factory = get_session_factory()
    session = factory()
    try:
        process_job(session, UUID(job_id), settings)
        return f"indexed:{job_id}"
    finally:
        session.close()
