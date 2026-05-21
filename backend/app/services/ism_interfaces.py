"""Выявление связей (интерфейсов) между документами ИСМ."""

from __future__ import annotations

import re
import uuid
from dataclasses import dataclass

from app.services.ism_structured import IsmDocumentStructured

_CROSS_DISCIPLINE = re.compile(
    r"раздел\w*\s+(АР|КР|КЖ|ОВ|ВК|ЭО|ТХ|СС|ПОС|ГП|ПЗ|ИОС|АС|ТМ)|"
    r"согласован\w*\s+с\s+раздел\w*\s+(АР|КР|КЖ|ОВ|ВК|ЭО|ТХ|СС|ПОС)",
    re.IGNORECASE,
)
_CODE_REF = re.compile(r"\b([A-ZА-Я]{1,4}[\-\u2013][A-ZА-Я0-9]{1,6}[\-\u2013][A-ZА-Я0-9.\-]{2,12})\b")


@dataclass
class IsmInterfaceLink:
    id: str
    source_filename: str
    target_filename: str | None
    target_discipline: str | None
    target_document_code: str | None
    reference_text: str
    link_type: str
    confidence: float


def detect_interfaces(
    documents: list[IsmDocumentStructured],
    full_texts: dict[str, str],
) -> list[IsmInterfaceLink]:
    by_discipline: dict[str, list[IsmDocumentStructured]] = {}
    by_code: dict[str, IsmDocumentStructured] = {}
    for doc in documents:
        if doc.discipline:
            by_discipline.setdefault(doc.discipline.upper(), []).append(doc)
        for code in doc.document_codes:
            by_code[code.upper()] = doc

    links: list[IsmInterfaceLink] = []
    seen: set[str] = set()

    for doc in documents:
        text = full_texts.get(doc.filename, "")
        if not text:
            continue
        for match in _CROSS_DISCIPLINE.finditer(text):
            target_disc = match.group(1).upper()
            target_doc = _pick_target(by_discipline.get(target_disc, []), doc.filename)
            key = f"{doc.filename}|disc|{target_disc}|{match.start()}"
            if key in seen:
                continue
            seen.add(key)
            links.append(
                IsmInterfaceLink(
                    id=uuid.uuid4().hex[:12],
                    source_filename=doc.filename,
                    target_filename=target_doc.filename if target_doc else None,
                    target_discipline=target_disc,
                    target_document_code=None,
                    reference_text=_snippet(text, match.start()),
                    link_type="discipline_ref",
                    confidence=0.85 if target_doc else 0.5,
                )
            )

        for code_match in _CODE_REF.finditer(text):
            code = code_match.group(1).upper()
            if code not in {c.upper() for c in doc.document_codes}:
                target = by_code.get(code)
                if target and target.filename == doc.filename:
                    continue
                key = f"{doc.filename}|code|{code}"
                if key in seen:
                    continue
                seen.add(key)
                links.append(
                    IsmInterfaceLink(
                        id=uuid.uuid4().hex[:12],
                        source_filename=doc.filename,
                        target_filename=target.filename if target else None,
                        target_discipline=target.discipline if target else None,
                        target_document_code=code,
                        reference_text=_snippet(text, code_match.start()),
                        link_type="document_code",
                        confidence=0.9 if target else 0.45,
                    )
                )

    return links


def _pick_target(candidates: list[IsmDocumentStructured], source: str) -> IsmDocumentStructured | None:
    for c in candidates:
        if c.filename != source:
            return c
    return candidates[0] if candidates else None


def _snippet(text: str, pos: int, radius: int = 90) -> str:
    start = max(0, pos - radius)
    end = min(len(text), pos + radius)
    return " ".join(text[start:end].split())
