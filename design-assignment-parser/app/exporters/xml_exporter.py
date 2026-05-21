"""Генерация XML из canonical JSON по mapping.yaml (без хардкода дерева в парсере)."""

from __future__ import annotations

from datetime import date
from uuid import uuid4
from xml.etree import ElementTree as ET

from app.models.canonical import DesignAssignmentCanonical
from app.schema_mapper.mapper import _get_by_path
from app.schema_mapper.registry import SchemaVersionInfo


def build_xml(canonical: DesignAssignmentCanonical, mapping: dict, schema_info: SchemaVersionInfo) -> str:
    """Собирает Document с обязательными атрибутами и заполненными полями из mapping."""
    doc_id = str(_get_by_path(canonical, "document.document_id") or uuid4())
    type_code = str(_get_by_path(canonical, "document.document_type_code") or schema_info.type_code)
    version = str(_get_by_path(canonical, "document.version_number") or 1)
    schema_ver = str(_get_by_path(canonical, "document.schema_version") or schema_info.schema_version)

    ns_xsi = "http://www.w3.org/2001/XMLSchema-instance"
    root = ET.Element(
        "Document",
        {
            "Id": doc_id,
            "TypeCode": type_code,
            "VersionNumber": str(version),
            "SchemaVersion": schema_ver,
            "{http://www.w3.org/2001/XMLSchema-instance}noNamespaceSchemaLocation": "DesignAssignment-01-00.xsd",
        },
    )
    root.set("xmlns:xsi", ns_xsi)
    if canonical.document.schema_url:
        root.set("SchemaLink", canonical.document.schema_url)

    requisites = ET.SubElement(root, "Requisites")
    _set_text(requisites, "Date", _fmt_date(canonical.document.document_date))
    _set_text(requisites, "Number", canonical.document.document_number or "б/н")
    _append_authors(requisites, canonical)
    ET.SubElement(requisites, "SecurityLabel").text = "0"

    content = ET.SubElement(root, "Content")
    _append_objective(content, canonical)
    _append_construction_object(content, canonical)

    ET.indent(root, space="  ")
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(root, encoding="unicode")


def _append_authors(requisites: ET.Element, canonical: DesignAssignmentCanonical) -> None:
    org = canonical.participants.author
    if not org.full_name:
        return
    authors = ET.SubElement(requisites, "Authors")
    author = ET.SubElement(authors, "Author")
    organization = ET.SubElement(author, "Organization")
    _set_text(organization, "FullName", org.full_name)
    if org.abbreviated_name:
        _set_text(organization, "AbbreviatedName", org.abbreviated_name)
    if org.inn:
        _set_text(organization, "INN", org.inn)
    if org.ogrn:
        _set_text(organization, "OGRN", org.ogrn)
    if org.kpp:
        _set_text(organization, "KPP", org.kpp)
    if canonical.participants.signer.surname:
        reps = ET.SubElement(author, "Representatives")
        rep = ET.SubElement(reps, "Representative", {"FunctionalRole": "1"})
        _set_text(rep, "Surname", canonical.participants.signer.surname)
        _set_text(rep, "Name", canonical.participants.signer.name or "")
        if canonical.participants.signer.patronymic:
            _set_text(rep, "Patronymic", canonical.participants.signer.patronymic)
        _set_text(rep, "Position", canonical.participants.signer.position or "")


def _append_objective(content: ET.Element, canonical: DesignAssignmentCanonical) -> None:
    texts = canonical.design_requirements.objective_text
    if not texts and canonical.requirements:
        texts = [canonical.requirements[0].text[:500]]
    if not texts:
        return
    obj = ET.SubElement(content, "Objective")
    for line in texts[:20]:
        _set_text(obj, "Text", line)


def _append_construction_object(content: ET.Element, canonical: DesignAssignmentCanonical) -> None:
    if not canonical.object.name:
        return
    container = ET.SubElement(content, "ConstructionObjects")
    co = ET.SubElement(container, "ConstructionObject", {"Code": canonical.object.code or "OBJ-001"})
    _set_text(co, "Name", canonical.object.name)
    if canonical.object.address_note:
        addr = ET.SubElement(co, "Address")
        _set_text(addr, "Note", canonical.object.address_note)


def _set_text(parent: ET.Element, tag: str, value: str | None) -> ET.Element:
    el = ET.SubElement(parent, tag)
    el.text = value or ""
    return el


def _fmt_date(value: date | None) -> str:
    if value is None:
        from datetime import date as d

        return d.today().isoformat()
    return value.isoformat()
