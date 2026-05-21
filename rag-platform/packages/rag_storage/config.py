from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = "postgresql+psycopg://rag:rag_secret@localhost:5432/rag_platform"
    redis_url: str = "redis://localhost:6379/0"

    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "ragminio"
    minio_secret_key: str = "ragminio_secret"
    minio_bucket: str = "documents"
    minio_secure: bool = False
    minio_region: str = "us-east-1"

    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: str | None = None
    qdrant_collection_text: str = "project_documents_text"

    embedding_model: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    embedding_dimension: int = 384
    embedding_use_sentence_transformers: bool = False

    parser_primary: str = "pypdf"
    parser_fallback: str = "pypdf"

    hybrid_search_enabled: bool = True
    rerank_enabled: bool = True
    hybrid_prefetch_limit: int = 30

    qdrant_collection_drawings_text: str = "project_drawings_text"
    qdrant_collection_project_analysis: str = "project_analysis_text"
    qdrant_collection_project_analysis_drawings: str = "project_analysis_drawings_text"
    qdrant_collection_ism_documents: str = "ism_documents"
    qdrant_collection_ism_requirements: str = "ism_requirements"
    qdrant_collection_ism_interfaces: str = "ism_interfaces"

    drawing_render_dpi: int = 200
    drawing_ocr_enabled: bool = True
    drawing_process_all_pdf_pages: bool = False
    drawing_index_enabled: bool = True
    ocr_language: str = "rus+eng"
    ocr_dpi: int = Field(default=300, ge=150, le=600)
    ocr_psm_modes: str = "3,6"
    ocr_min_text_layer_chars: int = Field(default=40, ge=0)

    max_upload_mb: int = 200

    ollama_base_url: str = "http://127.0.0.1:11434"
    ollama_model: str = "llama3.1:8b"
    ollama_timeout_seconds: int = 120
    openai_api_base: str = ""
    openai_api_key: str = ""
    llm_enabled: bool = True

    pilot_default_project_id: str = "PTE-ITC-450"


@lru_cache
def get_settings() -> Settings:
    return Settings()
