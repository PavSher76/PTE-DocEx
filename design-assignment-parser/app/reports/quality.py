from __future__ import annotations

import json
from pathlib import Path

from app.models.pipeline_state import PipelineJob, QualityGateResult
from app.schema_mapper.mapper import coverage_mandatory_fields


def run_quality_gates(job: PipelineJob, mapping: dict, ocr_threshold: float) -> list[QualityGateResult]:
    gates: list[QualityGateResult] = []
    gates.append(
        QualityGateResult(
            gate_id="G1",
            name="PDF readable",
            passed=job.source_pdf is not None and job.source_pdf.exists(),
            detail=str(job.source_pdf),
        )
    )
    avg_ocr = 0.0
    if job.pages:
        avg_ocr = sum(p.text_quality_score for p in job.pages) / len(job.pages)
    gates.append(
        QualityGateResult(
            gate_id="G2",
            name="OCR quality >= threshold",
            passed=avg_ocr >= ocr_threshold or job.pdf_type == "born_digital",
            detail=f"avg_quality={avg_ocr:.2f}",
        )
    )
    filled, total, missing = (0, 0, [])
    if job.canonical:
        filled, total, missing = coverage_mandatory_fields(job.canonical, mapping)
    gates.append(
        QualityGateResult(
            gate_id="G3",
            name="mandatory fields extracted",
            passed=total == 0 or filled / total >= 0.5,
            detail=f"{filled}/{total} missing={missing[:5]}",
        )
    )
    gates.append(
        QualityGateResult(
            gate_id="G4",
            name="XML generated",
            passed="design_assignment.xml" in job.artifacts,
        )
    )
    val = job.stage_metrics.get("validation")
    gates.append(
        QualityGateResult(
            gate_id="G5",
            name="XML validates against XSD",
            passed=bool(val and val.get("valid")),
            detail=str(val),
        )
    )
    trace_ok = bool(job.canonical and job.canonical.traceability)
    gates.append(
        QualityGateResult(
            gate_id="G6",
            name="traceability present",
            passed=trace_ok,
            detail=f"entries={len(job.canonical.traceability) if job.canonical else 0}",
        )
    )
    job.quality_gates = gates
    return gates


def write_quality_report_json(job: PipelineJob, path: Path) -> Path:
    payload = {
        "job_id": str(job.job_id),
        "pdf_type": job.pdf_type,
        "stages_completed": job.stages_completed,
        "quality_gates": [g.model_dump() for g in job.quality_gates],
        "errors": job.errors,
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path
