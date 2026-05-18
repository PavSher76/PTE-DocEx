"""Формирование JSON-контекста для локальных LLM по данным проекта (datacentric bundle)."""

from __future__ import annotations

import json
from typing import Any

from pydantic import BaseModel, Field

from app.project_context.domain_models import DesignAssignmentDraft

OFFICIAL_SCHEMA_PAGE = "https://minstroyrf.gov.ru/tim/xml-skhemy/zadanie-na-proektirovanie/p12_1/"


class InvestmentProjectNarratives(BaseModel):
    """Произвольные текстовые блоки для обогащения ИИ-контекста (вне формализованного XML)."""

    executive_summary: str = ""
    investment_model_and_payback: str = ""
    risks_and_constraints: str = ""
    stakeholders_and_governance: str = ""
    schedule_and_milestones: str = ""


class InvestmentProjectPackage(BaseModel):
    """Канонический пакет данных проекта: нарративы + формализованное задание для генерации документов."""

    narratives: InvestmentProjectNarratives = Field(default_factory=InvestmentProjectNarratives)
    assignment: DesignAssignmentDraft


def build_investment_project_ai_context(package: InvestmentProjectPackage) -> str:
    """Собирает компактный JSON для передачи в LLM (структура + пояснения)."""

    payload: dict[str, Any] = {
        "purpose": (
            "Datacentric-контекст инвестиционно-строительного проекта: качественные описания "
            "и формализованный набросок задания на проектирование для последующей генерации XML по схеме."
        ),
        "official_xml_schema": {
            "file_name": "DesignAssignment-01-00.xsd",
            "document_root": "Document",
            "document_type_code": "05.03",
            "schema_version_attribute": "01.00",
            "publication_page": OFFICIAL_SCHEMA_PAGE,
            "note": (
                "Формально утверждённая XML-схема размещается на сайте Минстроя России (раздел ТИМ). "
                "Итоговый XML необходимо проверять официальным или сертифицированным ПО "
                "в актуальной редакции схемы."
            ),
        },
        "narratives": package.narratives.model_dump(),
        "assignment_payload": package.assignment.model_dump(mode="json"),
        "model_instructions": (
            "Используй narratives как свободный контекст. Поле assignment_payload содержит данные, "
            "согласованные со структурой XML «Задание на проектирование». Не меняй коды видов "
            "документов и коды справочников без явной ссылки на НПА; уточняющие вопросы формулируй отдельным списком."
        ),
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)
