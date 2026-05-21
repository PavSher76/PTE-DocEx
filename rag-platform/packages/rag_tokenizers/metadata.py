"""Извлечение стадии, дисциплины, ревизии и статуса из инженерных документов."""

from __future__ import annotations

import re

STAGE_PATTERN = re.compile(r"\b(ОТР|ТЭО|ПД|РД)\b", re.IGNORECASE)
STAGE_MAP = {"ОТР": "OTR", "ТЭО": "TEO", "ПД": "PD", "РД": "RD"}

DOC_CODE_PATTERN = re.compile(
    r"\b([А-ЯЁ]{1,4}[-–][А-ЯЁ0-9]{1,8}(?:[-–][А-ЯЁ0-9]+)?)\b"
)
DISCIPLINE_BY_PREFIX = {
    "ТХ": "TX",
    "ОВ": "HV",
    "ВК": "WS",
    "ЭО": "EL",
    "ЭМ": "EL",
    "АР": "AR",
    "КЖ": "ST",
    "КМ": "ST",
    "ГП": "GP",
    "ПЗ": "GEN",
    "ИО": "IO",
    "СС": "SS",
    "ПОС": "POS",
    "ПБ": "PB",
    "ООС": "ENV",
}
REVISION_PATTERN = re.compile(
    r"(?:рев(?:изия)?|rev(?:ision)?)\s*[:№]?\s*([A-ZА-Я0-9]+)|изм\.?\s*(\d+)",
    re.IGNORECASE,
)
STATUS_PATTERN = re.compile(r"\b(IFC|IFA|IFD|AFC|AFU|AB|IFR)\b", re.IGNORECASE)
NTD_PATTERN = re.compile(
    r"\b(СП|ГОСТ(?:\s*Р)?|СанПиН|ФНП|СНиП)\s*[\d\.\-–]+(?:\s*[\d\.\-–]+)*",
    re.IGNORECASE,
)


def detect_stage(text: str, fallback: str | None = None) -> str | None:
    match = STAGE_PATTERN.search(text)
    if match:
        return STAGE_MAP.get(match.group(1).upper(), match.group(1).upper())
    return fallback


def detect_document_code(text: str) -> str | None:
    match = DOC_CODE_PATTERN.search(text)
    return match.group(1) if match else None


def detect_discipline(document_code: str | None, text: str = "") -> str | None:
    source = document_code or text
    if not source:
        return None
    upper = source.upper()
    for prefix, code in DISCIPLINE_BY_PREFIX.items():
        if f"-{prefix}" in upper or upper.startswith(f"{prefix}-") or f" {prefix}-" in upper:
            return code
        if upper.endswith(f"-{prefix}") or upper.startswith(prefix):
            return code
    return None


def detect_revision(text: str) -> str | None:
    match = REVISION_PATTERN.search(text)
    if not match:
        return None
    return match.group(1) or match.group(2)


def detect_status(text: str) -> str | None:
    match = STATUS_PATTERN.search(text)
    return match.group(1).upper() if match else None


def extract_ntd_refs(text: str) -> list[str]:
    return list({m.group(0).strip() for m in NTD_PATTERN.finditer(text)})
