"""Оркестратор: PDF → canonical JSON → XML → отчёты."""

from __future__ import annotations

import logging
import shutil
from datetime import datetime, timezone
from pathlib import Path

from app.config import Settings, get_settings
from app.exporters.json_exporter import (
    export_canonical_json,
    export_normalized_for_rag,
    export_requirements_json,
    export_traceability_json,
)
from app.exporters.rag_tokens import export_rag_tokens
from app.exporters.xml_exporter import build_xml
from app.extractors.fields import extract_fields
from app.extractors.requirements import extract_requirements
from app.extractors.sections import classify_blocks
from app.models.canonical import DesignAssignmentCanonical
from app.models.pipeline_state import JobStatus, PipelineJob
from app.ocr.extract import extract_pages
from app.parsers.pdf_type import detect_pdf_type, pages_to_layout_blocks
from app.pipeline.job_store import save_job
from app.reports.quality import run_quality_gates, write_quality_report_json
from app.reports.validation_report import write_validation_report_md
from app.schema_mapper.mapper import apply_corrections, coverage_mandatory_fields, normalize_canonical
from app.schema_mapper.registry import load_mapping, load_schema_version
from app.validators.xsd_validator import validate_xml_against_xsd

LOG = logging.getLogger("dap.pipeline")

STAGES = [
    "01_ingest_pdf",
    "02_detect_pdf_type",
    "03_extract_text_layer",
    "04_render_pages_to_images",
    "05_ocr_if_needed",
    "06_layout_detection",
    "07_extract_document_sections",
    "08_extract_fields",
    "09_normalize_values",
    "10_map_to_minstroy_schema",
    "11_generate_json",
    "12_generate_xml",
    "13_validate_xml_against_xsd",
    "14_generate_quality_report",
]


def run_pipeline(
    pdf_path: Path,
    *,
    settings: Settings | None = None,
    corrections_path: Path | None = None,
    job: PipelineJob | None = None,
) -> PipelineJob:
    settings = settings or get_settings()
    schema_info = load_schema_version(settings)
    mapping = load_mapping(settings)

    if job is None:
        job = PipelineJob(
            schema_version_key=schema_info.key,
            source_pdf=pdf_path,
            work_dir=settings.jobs_dir / str(pdf_path.stem),
        )
        job.work_dir.mkdir(parents=True, exist_ok=True)
    else:
        job.schema_version_key = schema_info.key
        if job.work_dir is None:
            job.work_dir = settings.jobs_dir / str(job.job_id)
            job.work_dir.mkdir(parents=True, exist_ok=True)
    job.status = JobStatus.running
    save_job(job)

    try:
        _stage(job, "01_ingest_pdf")
        dest = job.work_dir / pdf_path.name
        if pdf_path.resolve() != dest.resolve():
            shutil.copy2(pdf_path, dest)
        job.source_pdf = dest

        _stage(job, "02_detect_pdf_type")
        job.pdf_type, job.pages = detect_pdf_type(dest, settings)

        _stage(job, "03_extract_text_layer")
        pages_text = extract_pages(dest, settings)
        full_text = "\n\n".join(p.text for p in pages_text if p.text)

        _stage(job, "04_render_pages_to_images")
        _stage(job, "05_ocr_if_needed")
        job.stage_metrics["ocr_pages"] = sum(1 for p in pages_text if p.source == "tesseract_ocr")

        _stage(job, "06_layout_detection")
        blocks = pages_to_layout_blocks(pages_text)
        for page in job.pages:
            page.blocks = [b for b in blocks if b.page_number == page.page_number]

        _stage(job, "07_extract_document_sections")
        sections = classify_blocks(blocks)
        job.stage_metrics["sections"] = {k: len(v) for k, v in sections.items()}

        _stage(job, "08_extract_fields")
        canonical = DesignAssignmentCanonical()
        canonical.document.schema_url = schema_info.schema_url or canonical.document.schema_url
        canonical = extract_fields(canonical, blocks, full_text)
        canonical = extract_requirements(canonical, blocks, full_text)

        _stage(job, "09_normalize_values")
        if corrections_path:
            canonical = apply_corrections(canonical, corrections_path)
        canonical = normalize_canonical(canonical, mapping)
        filled, total, missing = coverage_mandatory_fields(canonical, mapping)
        job.stage_metrics["mandatory_coverage"] = {
            "filled": filled,
            "total": total,
            "missing": missing,
        }
        job.canonical = canonical

        _stage(job, "10_map_to_minstroy_schema")
        _stage(job, "11_generate_json")
        export_canonical_json(canonical, job.work_dir / "canonical.json")
        export_normalized_for_rag(canonical, job.work_dir / "normalized.json")
        export_requirements_json(canonical, job.work_dir / "requirements.json")
        export_traceability_json(canonical, job.work_dir / "traceability.json")
        job.artifacts["canonical.json"] = job.work_dir / "canonical.json"
        job.artifacts["requirements.json"] = job.work_dir / "requirements.json"
        job.artifacts["traceability.json"] = job.work_dir / "traceability.json"

        _stage(job, "12_generate_xml")
        xml_str = build_xml(canonical, mapping, schema_info)
        xml_path = job.work_dir / "design_assignment.xml"
        xml_path.write_text(xml_str, encoding="utf-8")
        job.artifacts["design_assignment.xml"] = xml_path

        _stage(job, "13_validate_xml_against_xsd")
        val = validate_xml_against_xsd(xml_path, schema_info.schema_path)
        job.stage_metrics["validation"] = val.__dict__
        write_validation_report_md(val, job.work_dir / "validation_report.md", schema_key=schema_info.key)
        job.artifacts["validation_report.md"] = job.work_dir / "validation_report.md"

        _stage(job, "14_generate_quality_report")
        export_rag_tokens(canonical, job.work_dir / "rag_tokens.json")
        job.artifacts["rag_tokens.json"] = job.work_dir / "rag_tokens.json"
        run_quality_gates(job, mapping, settings.ocr_quality_threshold)
        write_quality_report_json(job, job.work_dir / "quality_report.json")
        job.artifacts["quality_report.json"] = job.work_dir / "quality_report.json"

        job.status = JobStatus.completed
        LOG.info("job=%s completed gates=%s", job.job_id, [g.passed for g in job.quality_gates])
    except Exception as exc:
        job.status = JobStatus.failed
        job.errors.append(str(exc))
        LOG.exception("job=%s failed: %s", job.job_id, exc)
    finally:
        job.updated_at = datetime.now(timezone.utc)
        save_job(job)
    return job


def _stage(job: PipelineJob, name: str) -> None:
    job.stages_completed.append(name)
    LOG.info("job=%s ▶ %s", job.job_id, name)
