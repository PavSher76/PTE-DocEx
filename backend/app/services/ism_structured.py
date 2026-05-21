"""Структурирование метаданных документа ИСМ из текста и имени файла."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

_DISCIPLINE_IN_NAME = re.compile(
    r"(?:^|[_\-\s])(АР|КР|КЖ|ОВ|ВК|ЭО|ТХ|СС|ПОС|ГП|ПЗ|ИОС|АС|ТМ)(?:[_\-\s.]|$)",
    re.IGNORECASE,
)
_DOC_CODE = re.compile(
    r"\b([A-ZА-Я]{1,4}[\-\u2013][A-ZА-Я0-9]{1,6}[\-\u2013][A-ZА-Я0-9.\-]{2,12})\b",
)
_SECTION_REF = re.compile(
    r"(?:раздел\w*|том\w*|част\w*)\s+([A-ZА-Я]{2,5}|\d+(?:\.\d+)*)",
    re.IGNORECASE,
)
_DISCIPLINE_REF = re.compile(
    r"раздел\w*\s+(АР|КР|КЖ|ОВ|ВК|ЭО|ТХ|СС|ПОС|ГП|ПЗ|ИОС|АС|ТМ)",
    re.IGNORECASE,
)


@dataclass
class IsmDocumentStructured:
    filename: str
    relative_path: str
    file_type: str
    size_bytes: int
    discipline: str | None = None
    document_codes: list[str] = field(default_factory=list)
    section_hints: list[str] = field(default_factory=list)
    excerpt: str = ""
    chars_extracted: int = 0
    parse_status: str = "ok"
    parse_error: str | None = None
    document_id: str | None = None
    rag_job_status: str | None = None
    tokens_count: int = 0


def build_structured_document(
    path: Path,
    *,
    relative_path: str,
    text: str,
    parse_error: str | None = None,
) -> IsmDocumentStructured:
    filename = path.name
    suffix = path.suffix.lower().lstrip(".")
    doc = IsmDocumentStructured(
        filename=filename,
        relative_path=relative_path,
        file_type=suffix or "unknown",
        size_bytes=path.stat().st_size if path.is_file() else 0,
        chars_extracted=len(text),
        excerpt=text[:600].strip() if text else "",
        parse_status="failed" if parse_error else ("empty" if not text.strip() else "ok"),
        parse_error=parse_error,
    )
    if parse_error or not text.strip():
        _discipline_from_name(doc, filename)
        return doc

    codes = list(dict.fromkeys(_DOC_CODE.findall(text)))[:12]
    doc.document_codes = codes[:8]
    sections = list(dict.fromkeys(m.group(1) for m in _SECTION_REF.finditer(text)))[:10]
    doc.section_hints = sections

    name_match = _DISCIPLINE_IN_NAME.search(filename)
    if name_match:
        doc.discipline = name_match.group(1).upper()
    else:
        ref = _DISCIPLINE_REF.search(text[:4000])
        if ref:
            doc.discipline = ref.group(1).upper()

    return doc


def _discipline_from_name(doc: IsmDocumentStructured, filename: str) -> None:
    m = _DISCIPLINE_IN_NAME.search(filename)
    if m:
        doc.discipline = m.group(1).upper()
