from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS_ROOT = ROOT / "schemas" / "minstroy" / "design_assignment"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    active_minstroy_design_assignment_schema_version: str = "v01_00"
    jobs_dir: Path = Field(default=ROOT / "data" / "jobs")
    ocr_language: str = "rus+eng"
    ocr_dpi: int = Field(default=300, ge=150, le=600)
    ocr_psm_modes: str = "3,6"
    ocr_min_text_layer_chars: int = Field(default=40, ge=0)
    ocr_quality_threshold: float = Field(default=0.55, ge=0.0, le=1.0)
    mandatory_field_coverage_threshold: float = 0.85

    @property
    def schema_dir(self) -> Path:
        return SCHEMAS_ROOT / self.active_minstroy_design_assignment_schema_version


@lru_cache
def get_settings() -> Settings:
    return Settings()
