"""Токенизация требований из текста и layout-блоков."""

from __future__ import annotations

import re

from app.models.canonical import DesignAssignmentCanonical, RequirementRecord
from app.models.layout import LayoutBlock

REQ_LINE = re.compile(
    r"(?m)^\s*(?:\d+[\.\)]\s*)?("
    r"предусмотреть|обеспечить|выполнить|разработать|представить|соблюдать|учесть"
    r")[^\n]{10,500}",
    re.I,
)

TYPE_RULES: list[tuple[str, re.Pattern[str]]] = [
    ("ntd_requirement", re.compile(r"(?i)снип|сп\s+\d|гост|норматив")),
    ("engineering_survey_requirement", re.compile(r"(?i)изыскан")),
    ("source_data_requirement", re.compile(r"(?i)исходн")),
    ("digital_requirement", re.compile(r"(?i)bim|цифров|3d|тим")),
    ("safety_requirement", re.compile(r"(?i)безопасност")),
    ("operation_requirement", re.compile(r"(?i)эксплуатац")),
    ("design_scope_requirement", re.compile(r"(?i)раздел|состав\s+проект")),
]


def extract_requirements(
    canonical: DesignAssignmentCanonical,
    blocks: list[LayoutBlock],
    full_text: str,
) -> DesignAssignmentCanonical:
    seen: set[str] = set()
    counter = 0
    for block in blocks:
        for m in REQ_LINE.finditer(block.text):
            text = m.group(0).strip()
            norm = re.sub(r"\s+", " ", text)
            if norm in seen or len(norm) < 15:
                continue
            seen.add(norm)
            counter += 1
            req_type = _classify(norm)
            rec = RequirementRecord(
                requirement_id=f"REQ-{counter:06d}",
                type=req_type,  # type: ignore[arg-type]
                text=text,
                normalized_text=norm,
                source_page=block.page_number,
                bbox=block.bbox,
                confidence=min(0.95, block.confidence + 0.1),
                canonical_path=f"requirements[{counter - 1}]",
            )
            canonical.requirements.append(rec)

    # fallback: длинные абзацы из objective
    if not canonical.design_requirements.objective_text:
        for block in blocks[:30]:
            if len(block.text) > 80 and "задание" not in block.text.lower()[:40]:
                canonical.design_requirements.objective_text.append(block.text[:2000])
                break

    return canonical


def _classify(text: str) -> str:
    for name, pattern in TYPE_RULES:
        if pattern.search(text):
            return name
    return "customer_requirement"
