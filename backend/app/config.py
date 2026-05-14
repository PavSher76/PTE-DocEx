from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "PTE DocEx"
    api_prefix: str = "/api"
    database_url: str = "sqlite:///./storage/app.db"
    storage_dir: Path = Path("./storage")

    languagetool_url: str = "http://languagetool:8010/v2/check"
    languagetool_language: str = "ru-RU"

    ollama_base_url: str = "http://host.docker.internal:11434"
    ollama_model: str = "llama3.1:8b"
    ollama_timeout_seconds: float = 180.0

    ocr_language: str = "rus+eng"
    ocr_dpi: int = Field(default=300, ge=150, le=600)
    ocr_psm_modes: str = "3,6"
    ocr_use_text_layer: bool = True
    ocr_min_text_layer_chars: int = Field(default=40, ge=0)
    document_similarity_threshold: float = Field(default=0.985, ge=0.0, le=1.0)
    page_similarity_warning_threshold: float = Field(default=0.95, ge=0.0, le=1.0)
    max_upload_mb: int = 50

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    return Settings()
