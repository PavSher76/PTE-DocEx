"""Константы модуля Документы ИСМ."""

from __future__ import annotations

ISM_ALLOWED_SUFFIXES = frozenset({".pdf", ".doc", ".docx", ".xls", ".xlsx"})

ISM_DOCUMENT_TYPES = (
    "SOP",
    "FORM",
    "CHECKLIST",
    "REGISTER",
    "INSTRUCTION",
    "REQUIREMENT",
    "PROCESS_MAP",
    "TEMPLATE",
    "OTHER",
)

ISM_JOB_STATUSES = (
    "uploaded",
    "queued",
    "parsing",
    "extracting",
    "tokenizing",
    "embedding",
    "indexed",
    "failed",
    "needs_review",
    "cancelled",
)

ISM_ELEMENT_TYPES = (
    "metadata",
    "title",
    "section",
    "subsection",
    "paragraph",
    "table",
    "form_field",
    "checklist_item",
    "requirement",
    "responsibility",
    "input_data",
    "output_data",
    "process_step",
    "reference",
    "appendix",
)

ISM_TOKEN_TYPES = (
    "process_description",
    "process_step",
    "input_data",
    "output_data",
    "responsibility",
    "requirement",
    "control_point",
    "checklist_item",
    "form_template",
    "document_reference",
    "risk",
    "kpi",
    "lesson_learned",
    "metadata",
)

ISM_LINK_TYPES = (
    "references",
    "requires_input_from",
    "produces_output_for",
    "controls",
    "approves",
    "duplicates",
    "conflicts",
    "supersedes",
    "discipline_ref",
    "document_code",
)

DEFAULT_ISM_PROCESSES: list[dict[str, str | list[str] | None]] = [
    {
        "process_code": "ISM-CHANGE",
        "process_name": "Управление изменениями",
        "owner": "ИСМ",
        "description": "Контроль и согласование изменений в проектной документации.",
        "related_disciplines": [],
    },
    {
        "process_code": "ISM-SOP",
        "process_name": "Разработка SOP",
        "owner": "ИСМ",
        "description": "Стандартные операционные процедуры.",
        "related_disciplines": ["TX", "АР", "КР"],
    },
    {
        "process_code": "ISM-SOURCE",
        "process_name": "Проверка исходных данных",
        "owner": "ИСМ",
        "description": "Верификация входных данных для проектирования.",
        "related_disciplines": [],
    },
    {
        "process_code": "ISM-NCR",
        "process_name": "Управление несоответствиями",
        "owner": "ИСМ",
        "description": "Регистрация и закрытие несоответствий.",
        "related_disciplines": [],
    },
    {
        "process_code": "ISM-LL",
        "process_name": "Lessons Learned",
        "owner": "ИСМ",
        "description": "Сессии выученных уроков.",
        "related_disciplines": [],
    },
    {
        "process_code": "ISM-QC",
        "process_name": "Нормоконтроль",
        "owner": "ИСМ",
        "description": "Нормоконтроль проектной продукции.",
        "related_disciplines": [],
    },
    {
        "process_code": "ISM-REQ",
        "process_name": "Управление требованиями",
        "owner": "ИСМ",
        "description": "Трассировка и контроль требований.",
        "related_disciplines": [],
    },
]
