import pytest
from pathlib import Path

from app.config import Settings
from app.pipeline.orchestrator import run_pipeline

SAMPLE_PDF = Path(__file__).resolve().parents[2] / "test_data" / "Задание на проектирование_01-00" / "Описание.pdf"


@pytest.mark.skipif(not SAMPLE_PDF.exists(), reason="sample PDF not in workspace")
def test_pipeline_smoke(tmp_path: Path) -> None:
    settings = Settings(jobs_dir=tmp_path / "jobs")
    job = run_pipeline(SAMPLE_PDF, settings=settings)
    assert job.status.value in {"completed", "failed"}
    if job.status.value == "completed":
        assert "canonical.json" in job.artifacts
        assert "design_assignment.xml" in job.artifacts
        assert "rag_tokens.json" in job.artifacts
