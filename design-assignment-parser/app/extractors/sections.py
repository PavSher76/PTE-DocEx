"""Сегментация документа по разделам (заголовки, приложения)."""

from __future__ import annotations

import re

from app.models.layout import LayoutBlock

SECTION_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("objective", re.compile(r"(?im)^\s*(цель|задач[аи])\s+(проектирования|работ)")),
    ("decision_documents", re.compile(r"(?im)документ[ы]?\s*[-–]?\s*основан")),
    ("source_data", re.compile(r"(?im)исходн[а-я\s]+данн")),
    ("engineering_surveys", re.compile(r"(?im)инженерн[а-я\s]+изыскан")),
    ("ntd", re.compile(r"(?im)(нормативн|нтд|снип|сп\s+\d)")),
    ("design_stage", re.compile(r"(?im)(стади[яи]\s+проектирования|проектная\s+документация|рабочая\s+документация)")),
    ("appendix", re.compile(r"(?im)^\s*приложени[ея]\s*№?\s*\d*")),
]


def classify_blocks(blocks: list[LayoutBlock]) -> dict[str, list[LayoutBlock]]:
    sections: dict[str, list[LayoutBlock]] = {key: [] for key, _ in SECTION_PATTERNS}
    sections["body"] = []
    current = "body"
    for block in blocks:
        for key, pattern in SECTION_PATTERNS:
            if pattern.search(block.text[:200]):
                current = key
                break
        sections.setdefault(current, []).append(block)
    return sections
