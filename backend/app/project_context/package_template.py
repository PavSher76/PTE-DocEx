"""Минимально валидный пакет данных для старта редактирования в UI и тестов."""

from __future__ import annotations

from datetime import date

from app.project_context.ai_bundle import InvestmentProjectNarratives, InvestmentProjectPackage
from app.project_context.domain_models import (
    ConstructionObjectDraft,
    DecisionDocRef,
    DesignAssignmentDraft,
    LegalEntityOrg,
    OfficialPersonRu,
    SurveyWorkPackage,
)


def default_investment_project_package() -> InvestmentProjectPackage:
    org_tc = LegalEntityOrg(
        full_name='Общество с ограниченной ответственностью «Технический заказчик»',
        abbreviated_name='ООО «ТехЗаказчик»',
        ogrn="1027700132195",
        inn="7707083893",
        kpp="770701001",
    )
    org_author = LegalEntityOrg(
        full_name='Общество с ограниченной ответственностью «Автор документа»',
        ogrn="1027700132196",
        inn="7707083894",
        kpp="770701002",
    )
    signer = OfficialPersonRu(
        surname="Иванов",
        name="Иван",
        patronymic="Иванович",
        position="Главный инженер проекта",
    )
    draft = DesignAssignmentDraft(
        issue_date=date.today(),
        document_number="ЗНП-001",
        author_organization=org_author,
        signer=signer,
        technical_customer=org_tc,
        decision_documents=[
            DecisionDocRef(
                xml_id="doc_tp",
                type_code="03.01",
                name="Документ территориального планирования",
                number="1",
                issued_on=date.today(),
                author_note="Утверждён органом местного самоуправления",
                web_link="https://example.invalid/tp",
            ),
        ],
        initial_documents=[
            DecisionDocRef(
                xml_id="doc_gpun",
                type_code="04.01",
                name="Градостроительный план земельного участка",
                number="ГПЗУ-1",
                issued_on=date.today(),
                author_note="Орган исполнительной власти субъекта РФ",
                web_link="https://example.invalid/gpzu",
            ),
        ],
        objective_paragraphs=["Цель проекта (заполните)."],
        quality_solution_paragraphs=["Требования к качеству и ресурсосбережению (заполните)."],
        marginal_cost_paragraphs=["Предельная стоимость / порядок определения (заполните)."],
        pd_tasks=["Разработать проектную документацию."],
        rd_tasks=None,
        surveys=SurveyWorkPackage(
            survey_region_code="77",
            survey_area_description="Описание района изысканий",
            survey_types=[1, 2],
        ),
        construction_object=ConstructionObjectDraft(
            code="OKS-001",
            name="Наименование объекта капитального строительства",
            address_region_code="77",
            address_note="Адрес или местоположение (неформализованное описание)",
            object_kind=2,
            construction_kind=1,
            functions_class_code="01.02.003.004",
        ),
    )
    return InvestmentProjectPackage(
        narratives=InvestmentProjectNarratives(
            executive_summary="Краткая инвестиционная и производственная суть проекта.",
        ),
        assignment=draft,
    )
