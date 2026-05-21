"""Парсинг документов ИСМ в структурные элементы."""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from app.config import Settings
from app.ism.constants import ISM_ELEMENT_TYPES
from app.services.ism_extract import extract_ism_text

_HEADING = re.compile(r"^(?:\d+(?:\.\d+)*[\.\)]?\s+|[IVXLC]+\.\s+)(.+)$", re.MULTILINE)
_REQUIREMENT = re.compile(
    r"(?:должен|должна|должны|необходимо|требуется|обязан|запрещено|не допускается)",
    re.IGNORECASE,
)
_SOP_REF = re.compile(
    r"(?:см\.?\s*|согласно\s+|в соответствии с\s+)(SOP[\-\w./]+|Форма[\s\-–—\w./]+|"
    r"Чек[\-\s]?лист[\s\-–—\w./]+|Реестр[\s\-–—\w./]+|Приложение\s+[\w.\-]+)",
    re.IGNORECASE,
)
_PROCESS_STEP = re.compile(r"^\s*(\d+[\.\)])\s+(.+)$", re.MULTILINE)
_CODE_IN_NAME = re.compile(r"(SOP[\-\w]+|ISM[\-\w]+)", re.IGNORECASE)


@dataclass
class ParsedElement:
    element_type: str
    section: str
    text: str
    source_page: int | None = None
    source_table: str | None = None
    bbox: list[float] | dict | None = None
    extra: dict = field(default_factory=dict)


@dataclass
class ParseResult:
    full_text: str
    elements: list[ParsedElement] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
    requirements: list[str] = field(default_factory=list)
    references: list[str] = field(default_factory=list)


def parse_file(path, settings: Settings, *, filename: str) -> ParseResult:
    suffix = path.suffix.lower() if hasattr(path, "suffix") else ""
    if suffix == ".pdf":
        from app.ism.parse_pdf import parse_pdf_with_layout

        return parse_pdf_with_layout(path, settings, filename=filename)
    text = extract_ism_text(path, settings)
    return structure_text(text, filename=filename)


def structure_text(text: str, *, filename: str) -> ParseResult:
    result = ParseResult(full_text=text)
    if not text.strip():
        return result

    code_match = _CODE_IN_NAME.search(filename)
    result.metadata = {
        "filename": filename,
        "chars": len(text),
        "detected_code": code_match.group(1).upper() if code_match else None,
    }

    current_section = ""
    lines = text.splitlines()
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        hm = _HEADING.match(stripped)
        if hm:
            current_section = hm.group(1).strip()[:128]
            result.elements.append(
                ParsedElement("section", current_section, stripped, extra={"level": "heading"})
            )
            continue
        pm = _PROCESS_STEP.match(stripped)
        if pm:
            result.elements.append(
                ParsedElement(
                    "process_step",
                    current_section,
                    stripped,
                    extra={"step": pm.group(1)},
                )
            )
            continue
        if _REQUIREMENT.search(stripped):
            result.requirements.append(stripped)
            result.elements.append(ParsedElement("requirement", current_section, stripped))
            continue
        if len(stripped) > 20 and "|" in stripped and stripped.count("|") >= 2:
            result.elements.append(
                ParsedElement("table", current_section, stripped, source_table=current_section or "table")
            )
            continue
        result.elements.append(ParsedElement("paragraph", current_section, stripped))

    for ref in _SOP_REF.finditer(text):
        result.references.append(ref.group(0).strip())

    if not any(e.element_type == "title" for e in result.elements):
        title_line = lines[0].strip() if lines else filename
        result.elements.insert(0, ParsedElement("title", "", title_line[:512]))

    return result


def guess_document_type(filename: str, text: str) -> str:
    lower = (filename + " " + text[:2000]).lower()
    if "чек" in lower and "лист" in lower:
        return "CHECKLIST"
    if "реестр" in lower:
        return "REGISTER"
    if "форма" in lower:
        return "FORM"
    if "sop" in lower or "стандартн" in lower and "операц" in lower:
        return "SOP"
    if "инструкц" in lower:
        return "INSTRUCTION"
    if "требован" in lower:
        return "REQUIREMENT"
    return "OTHER"
