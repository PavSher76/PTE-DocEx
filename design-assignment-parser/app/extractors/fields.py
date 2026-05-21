"""Извлечение реквизитов и полей в canonical JSON."""

from __future__ import annotations

import re
from datetime import date

from app.models.canonical import DesignAssignmentCanonical
from app.models.layout import LayoutBlock

INN_RE = re.compile(r"\bИНН\s*[:№]?\s*(\d{10})\b", re.I)
OGRN_RE = re.compile(r"\bОГРН\s*[:№]?\s*(\d{13})\b", re.I)
KPP_RE = re.compile(r"\bКПП\s*[:№]?\s*(\d{9})\b", re.I)
DATE_RE = re.compile(r"\b(\d{2})[./](\d{2})[./](\d{4})\b")
DOC_NUM_RE = re.compile(r"(?im)(?:№|номер)\s*[:№]?\s*([^\n\r]{1,40})")
OBJECT_RE = re.compile(
    r"(?im)(?:объект\s+капитального\s+строительства|наименование\s+объекта|объект)\s*[:–-]?\s*(.+?)(?:\n|$)",
)
ADDRESS_RE = re.compile(r"(?im)(?:место\s+расположения|адрес)\s*[:–-]?\s*(.+?)(?:\n|$)")
CADASTR_RE = re.compile(r"\b(\d{2}:\d{2}:\d{6,7}:\d+)\b")


def extract_fields(
    canonical: DesignAssignmentCanonical,
    blocks: list[LayoutBlock],
    full_text: str,
) -> DesignAssignmentCanonical:
    canonical.ensure_document_id()

    # Реквизиты
    for m in DATE_RE.finditer(full_text[:3000]):
        try:
            d = date(int(m.group(3)), int(m.group(2)), int(m.group(1)))
            if not canonical.document.document_date:
                canonical.document.document_date = d
                canonical.add_trace("document.document_date", d.isoformat(), confidence=0.75)
            break
        except ValueError:
            continue

    m = DOC_NUM_RE.search(full_text[:4000])
    if m:
        num = m.group(1).strip()
        canonical.document.document_number = num
        canonical.add_trace("document.document_number", num, confidence=0.7)

    for pattern, path, setter in (
        (INN_RE, "participants.author.inn", lambda v: setattr(canonical.participants.author, "inn", v)),
        (OGRN_RE, "participants.author.ogrn", lambda v: setattr(canonical.participants.author, "ogrn", v)),
        (KPP_RE, "participants.author.kpp", lambda v: setattr(canonical.participants.author, "kpp", v)),
    ):
        hit = pattern.search(full_text)
        if hit:
            setter(hit.group(1))
            canonical.add_trace(path, hit.group(1), confidence=0.85, method="regex")

    org = re.search(
        r"(?im)(?:полное\s+наименование|организация|застройщик|технический\s+заказчик)\s*[:–-]?\s*"
        r"((?:ООО|АО|ПАО|Акционерное\s+общество)[^\n]{5,200})",
        full_text,
    )
    if org:
        name = org.group(1).strip()
        canonical.participants.author.full_name = name
        canonical.add_trace("participants.author.full_name", name, confidence=0.65)

    mobj = OBJECT_RE.search(full_text)
    if mobj:
        canonical.object.name = mobj.group(1).strip()[:500]
        canonical.add_trace("object.name", canonical.object.name, confidence=0.6)

    aobj = ADDRESS_RE.search(full_text)
    if aobj:
        canonical.object.address_note = aobj.group(1).strip()[:500]
        canonical.object.address = canonical.object.address_note
        canonical.add_trace("object.address_note", canonical.object.address_note, confidence=0.6)

    canonical.object.cadastre_numbers = list(dict.fromkeys(CADASTR_RE.findall(full_text)))

    if not canonical.object.code:
        canonical.object.code = "OBJ-001"

    if re.search(r"(?im)проектная\s+документация", full_text):
        canonical.design_requirements.stage = "PD"
    elif re.search(r"(?im)рабочая\s+документация", full_text):
        canonical.design_requirements.stage = "RD"

    return canonical
