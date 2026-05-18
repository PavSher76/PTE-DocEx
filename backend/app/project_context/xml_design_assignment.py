"""Сборка XML «Задание на проектирование» по XML-схеме Минстроя России DesignAssignment-01-00.xsd."""

from __future__ import annotations

from datetime import date
from uuid import uuid4
from xml.etree import ElementTree as ET

from app.project_context.domain_models import (
    ConstructionObjectDraft,
    DecisionDocRef,
    DesignAssignmentDraft,
    LegalEntityOrg,
    OfficialPersonRu,
)

_SURVEY_TYPE_TO_RESULT_DOC: dict[int, str] = {
    1: "06.01",
    2: "06.02",
    3: "06.03",
    4: "06.04",
    5: "06.05",
    6: "06.06",
    7: "06.07",
    8: "06.08",
    9: "06.09",
    10: "06.10",
    11: "06.11",
}


def _xs_bool(value: bool) -> str:
    return "true" if value else "false"


def _iso_date(value: date) -> str:
    return value.isoformat()


def _sub(parent: ET.Element, tag: str, text: str | None = None, **attrib: str | int | bool) -> ET.Element:
    normalized = {k: str(v) for k, v in attrib.items()}
    el = ET.SubElement(parent, tag, attrib=normalized)
    if text is not None:
        el.text = text
    return el


def _append_text_paragraphs(parent: ET.Element, paragraphs: list[str]) -> None:
    for line in paragraphs:
        _sub(parent, "Text", line)


def _organization(org: LegalEntityOrg) -> ET.Element:
    el = ET.Element("Organization")
    _sub(el, "FullName", org.full_name)
    if org.abbreviated_name:
        _sub(el, "AbbreviatedName", org.abbreviated_name)
    _sub(el, "OGRN", org.ogrn)
    _sub(el, "INN", org.inn)
    _sub(el, "KPP", org.kpp)
    return el


def _official_person(person: OfficialPersonRu) -> tuple[ET.Element, ET.Element, ET.Element | None]:
    s = ET.Element("Surname")
    s.text = person.surname
    n = ET.Element("Name")
    n.text = person.name
    if person.patronymic:
        p = ET.Element("Patronymic")
        p.text = person.patronymic
        return (s, n, p)
    return (s, n, None)


def _representative(signer: OfficialPersonRu, functional_role: int = 1) -> ET.Element:
    rep = ET.Element("Representative", FunctionalRole=str(functional_role))
    sur, nam, pat = _official_person(signer)
    rep.append(sur)
    rep.append(nam)
    if pat is not None:
        rep.append(pat)
    _sub(rep, "Position", signer.position)
    return rep


def _authors_block(org: LegalEntityOrg, signer: OfficialPersonRu) -> ET.Element:
    authors = ET.Element("Authors")
    author = ET.SubElement(authors, "Author")
    author.append(_organization(org))
    reps = ET.SubElement(author, "Representatives")
    reps.append(_representative(signer))
    return authors


def _document_infos(parent: ET.Element, docs: list[DecisionDocRef]) -> None:
    for doc in docs:
        info = ET.SubElement(parent, "DocumentInfo", attrib={"Id": doc.xml_id, "Type": doc.type_code})
        _sub(info, "Name", doc.name)
        _sub(info, "Number", doc.number)
        _sub(info, "Date", _iso_date(doc.issued_on))
        _sub(info, "AuthorNote", doc.author_note)
        _sub(info, "WebLink", doc.web_link)


def _address(region_code: str, note: str) -> ET.Element:
    addr = ET.Element("Address")
    _sub(addr, "RegionCode", region_code)
    _sub(addr, "Note", note)
    return addr


def _survey_default_note(kind: int, pkg: DesignAssignmentDraft) -> list[str]:
    if kind == 1 and pkg.surveys.geodesy_note:
        return [pkg.surveys.geodesy_note.strip()]
    if kind == 2 and pkg.surveys.geology_note:
        return [pkg.surveys.geology_note.strip()]
    return [
        "Состав, объём и методика работ определяются действующими нормами РФ "
        "и особенностями объекта; результаты должны обеспечивать безопасность "
        "и надёжность последующих проектных решений.",
    ]


def _engineering_survey_block(pkg: DesignAssignmentDraft) -> ET.Element:
    es = ET.Element("EngineeringSurvey")
    intro = [
        "Необходимо выполнить инженерные изыскания и предоставить результаты в составе, "
        "достаточном для разработки проектной документации по объекту.",
    ]
    common = ET.SubElement(es, "Common")
    _append_text_paragraphs(common, intro)

    addr = ET.SubElement(es, "Address")
    _sub(addr, "RegionCode", pkg.surveys.survey_region_code.strip())
    _sub(addr, "District", pkg.surveys.survey_area_description.strip())

    reqs = ET.SubElement(es, "SurveysRequirements")
    for kind in pkg.surveys.survey_types:
        survey_el = ET.SubElement(reqs, "Survey", Type=str(kind))
        req_wrap = ET.SubElement(survey_el, "Requirements")
        _append_text_paragraphs(req_wrap, _survey_default_note(kind, pkg))

    doc_req = ET.SubElement(es, "DocumentsRequirements")
    for kind in sorted(set(pkg.surveys.survey_types)):
        doc_el = ET.SubElement(doc_req, "Document", Type=_SURVEY_TYPE_TO_RESULT_DOC[kind])
        doc_req_inner = ET.SubElement(doc_el, "Requirements")
        _append_text_paragraphs(
            doc_req_inner,
            [f"Требования к содержанию и оформлению документов по виду {kind}."],
        )

    return es


def _object_xml(obj: ConstructionObjectDraft, project_documents_wrapper: str) -> ET.Element:
    object_el = ET.Element(
        "Object",
        attrib={
            "Code": obj.code,
            "SecurityInfluence": _xs_bool(False),
            "DangerousIndustrialObject": "Не относится к опасным производственным объектам",
            "FireDangerCategory": "Категория не устанавливается",
            "PeoplePermanentStay": _xs_bool(False),
            "ResponsibilityLevel": "нормальный",
            "Placement": "1",
            "IsCulturalHeritage": _xs_bool(False),
        },
    )
    _sub(object_el, "Name", obj.name)
    object_el.append(_address(obj.address_region_code, obj.address_note))
    _sub(object_el, "ObjectType", text=str(obj.object_kind))
    _sub(object_el, "ConstructionType", text=str(obj.construction_kind))
    _sub(object_el, "FunctionsClass", obj.functions_class_code)

    poi = ET.SubElement(object_el, "POI")
    _sub(poi, "Name", obj.capacity_indicator_name)
    _sub(poi, "Measure", obj.capacity_measure_okei)
    _sub(poi, "Value", obj.capacity_indicator_value)

    solutions = ET.SubElement(object_el, "ProjectSolutions")
    _sub(solutions, "TechnologicalSolutions")

    pd_el = ET.SubElement(object_el, "ProjectDocuments")
    wrapper = ET.SubElement(pd_el, project_documents_wrapper)
    ET.SubElement(wrapper, "ProjectDocumentation")

    return object_el


def build_minstroy_design_assignment_xml(draft: DesignAssignmentDraft) -> str:
    """Формирует XML-документ без целевого пространства имён (как в официальной схеме).

    Ограничение текущей реализации: поддерживаются только объекты с ``object_kind`` 1 или 2;
    для линейного объекта необходимо расширить формирование адресов и блока ``ProjectSolutions``.
    """

    obj_kind = draft.construction_object.object_kind
    if obj_kind == 3:
        msg = (
            "Линейный объект (ObjectType=3) требует парных элементов BeginAddress/FinalAddress "
            "и отдельного набора требований ProjectSolutions — расширьте сборщик при необходимости."
        )
        raise ValueError(msg)

    wrapper_tag = "IndustrialObject" if obj_kind == 1 else "NotIndustrialObject"

    doc_id = draft.document_uuid or uuid4()
    root = ET.Element(
        "Document",
        attrib={
            "Id": str(doc_id),
            "TypeCode": "05.03",
            "VersionNumber": str(draft.version_number),
            "SchemaVersion": "01.00",
            **({"SchemaLink": draft.schema_link} if draft.schema_link else {}),
        },
    )

    req = ET.SubElement(root, "Requisites")
    _sub(req, "Date", _iso_date(draft.issue_date))
    _sub(req, "Number", draft.document_number)
    req.append(_authors_block(draft.author_organization, draft.signer))
    _sub(req, "SecurityLabel", str(draft.security_label))

    content = ET.SubElement(root, "Content")
    objective = ET.SubElement(content, "Objective")
    _append_text_paragraphs(objective, draft.objective_paragraphs)

    dd = ET.SubElement(content, "DecisionDocuments")
    _document_infos(dd, draft.decision_documents)

    if draft.developer is not None:
        dev_root = ET.SubElement(content, "Developers")
        dev_root.append(_organization(draft.developer))

    if draft.technical_customer is not None:
        tc_root = ET.SubElement(content, "TechnicalCustomer")
        tc_root.append(_organization(draft.technical_customer))

    designers = ET.SubElement(content, "Designers")
    req_blk = ET.SubElement(designers, "Requirements")
    _sub(
        req_blk,
        "Requirement",
        "Разработчик проектной документации определяется заказчиком; сведения о конкретной организации "
        "вносятся при заключении договора (не конфликтуют с отсутствием блока Designer в данном шаблоне).",
    )

    fin = ET.SubElement(content, "FinanceSources")
    budget = ET.SubElement(fin, "Budget")
    _sub(budget, "Level", str(draft.finance_budget_level))

    qs = ET.SubElement(content, "QualitySolutions")
    _append_text_paragraphs(qs, draft.quality_solution_paragraphs)

    mc = ET.SubElement(content, "MarginalCost")
    _append_text_paragraphs(mc, draft.marginal_cost_paragraphs)

    phases = ET.SubElement(content, "DesignPhases")
    pd_phase = ET.SubElement(phases, "DesignPhase", Phase="1")
    for task in draft.pd_tasks:
        _sub(pd_phase, "Task", task)
    if draft.rd_tasks:
        rd_phase = ET.SubElement(phases, "DesignPhase", Phase="2")
        for task in draft.rd_tasks:
            _sub(rd_phase, "Task", task)

    content.append(ET.Element("Land"))

    init_docs = ET.SubElement(content, "InitialDocuments")
    _document_infos(init_docs, draft.initial_documents)

    content.append(_engineering_survey_block(draft))
    content.append(_object_xml(draft.construction_object, wrapper_tag))

    ET.indent(root, space="  ")
    xml_bytes = ET.tostring(root, encoding="utf-8", xml_declaration=True)
    return xml_bytes.decode("utf-8")
