"""Типизированный набросок для XML-сборки по XML-схеме Минстроя «Задание на проектирование» (DesignAssignment-01-00.xsd)."""

from __future__ import annotations

import re
from datetime import date
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, model_validator

CYRILLIC_FIO_RE = re.compile(r"^[а-яА-ЯёЁ\-\s]+$")

_ObjectKind = Literal[1, 2, 3]
_ConstructionKind = Literal[1, 2, 3, 4, 5]
_BudgetLevel = Literal[1, 2, 3, 4, 5]


class LegalEntityOrg(BaseModel):
    """Юридическое лицо в составе XML-документа."""

    full_name: str = Field(min_length=1, max_length=4000)
    abbreviated_name: str | None = Field(default=None, max_length=4000)
    ogrn: str = Field(description="13 цифр")
    inn: str = Field(description="10 цифр юридического лица")
    kpp: str = Field(description="9 цифр")

    @staticmethod
    def _digits(value: str, length: int) -> str:
        if len(value) != length or not value.isdigit():
            raise ValueError(f"Ожидалась строка из {length} цифр.")
        return value

    @field_validator("ogrn")
    @classmethod
    def check_ogrn(cls, v: str) -> str:
        return cls._digits(v.strip(), 13)

    @field_validator("inn")
    @classmethod
    def check_inn(cls, v: str) -> str:
        return cls._digits(v.strip(), 10)

    @field_validator("kpp")
    @classmethod
    def check_kpp(cls, v: str) -> str:
        return cls._digits(v.strip(), 9)


class OfficialPersonRu(BaseModel):
    """Подписант с ФИО на кириллице (требование схемы к элементам ФИО)."""

    surname: str = Field(min_length=1)
    name: str = Field(min_length=1)
    patronymic: str | None = None
    position: str = Field(min_length=1)

    @field_validator("surname", "name")
    @classmethod
    def _cyr(cls, v: str) -> str:
        v = v.strip()
        if not CYRILLIC_FIO_RE.match(v):
            raise ValueError("ФИО должно содержать только кириллицу, пробелы и дефис.")
        return v

    @field_validator("patronymic")
    @classmethod
    def _cyr_pat(cls, v: str | None) -> str | None:
        if v is None:
            return None
        v = v.strip()
        if not CYRILLIC_FIO_RE.match(v):
            raise ValueError("Отчество должно содержать только кириллицу, пробелы и дефис.")
        return v


class DecisionDocRef(BaseModel):
    """Ссылка на документ-основание для блоков DecisionDocuments и InitialDocuments."""

    xml_id: str = Field(min_length=1, pattern=r"^[A-Za-z_][\w.\-]*$")
    type_code: str = Field(min_length=5, max_length=5)
    name: str = Field(min_length=1)
    number: str = Field(min_length=1)
    issued_on: date
    author_note: str = Field(min_length=1)
    web_link: str = Field(min_length=8)


class SurveyWorkPackage(BaseModel):
    """Набор инженерных изысканий для ветки «необходимо выполнить ИИ»."""

    survey_region_code: str = Field(description="Код региона по справочнику RegionCode схемы")
    survey_area_description: str = Field(min_length=1, description="District — описание района изысканий")
    survey_types: list[int] = Field(min_length=1)
    geodesy_note: str | None = None
    geology_note: str | None = None

    @field_validator("survey_types")
    @classmethod
    def _survey_codes(cls, values: list[int]) -> list[int]:
        for v in values:
            if v < 1 or v > 11:
                raise ValueError("Код вида инженерных изысканий должен быть в диапазоне 1–11.")
        return values


class ConstructionObjectDraft(BaseModel):
    """Обязательные атрибуты и поля объекта капитального строительства."""

    code: str = Field(min_length=1, pattern=r"^[0-9A-Za-zА-Яа-я_-]+$")
    name: str = Field(min_length=1)
    address_region_code: str
    address_note: str = Field(min_length=1, description="Неформализованный адрес в элементе Address/Note")
    object_kind: _ObjectKind
    construction_kind: _ConstructionKind
    functions_class_code: str
    capacity_indicator_name: str = Field(default="Проектная мощность", min_length=1)
    capacity_indicator_value: str = Field(default="—", min_length=1)
    capacity_measure_okei: str = Field(default="796", description="Код ОКЕИ по справочнику схемы")

    @field_validator("functions_class_code")
    @classmethod
    def _fn_cls_oks(cls, v: str) -> str:
        if not re.match(r"^\d{1,2}\.\d{1,2}\.\d{1,3}\.\d{1,3}$", v.strip()):
            raise ValueError(
                "Код функционального класса ОКС должен соответствовать шаблону XX.XX.XXX.XXX "
                "(классификатор функциональных назначений)."
            )
        return v.strip()


class DesignAssignmentDraft(BaseModel):
    """Данные для формирования корня Document с фиксированными кодами вида 05.03 и версией схемы 01.00."""

    document_uuid: UUID | None = None
    version_number: int = Field(default=1, ge=1)
    schema_link: str | None = Field(
        default=None,
        description="Рекомендуется URL страницы XML-схем на сайте Минстроя РФ",
    )
    issue_date: date
    document_number: str = Field(min_length=1)
    author_organization: LegalEntityOrg
    signer: OfficialPersonRu
    security_label: Literal[0, 1] = 0
    developer: LegalEntityOrg | None = None
    technical_customer: LegalEntityOrg | None = None
    finance_budget_level: _BudgetLevel = 1
    decision_documents: list[DecisionDocRef] = Field(min_length=1)
    initial_documents: list[DecisionDocRef] = Field(min_length=1)
    objective_paragraphs: list[str] = Field(min_length=1)
    quality_solution_paragraphs: list[str] = Field(min_length=1)
    marginal_cost_paragraphs: list[str] = Field(min_length=1)
    pd_tasks: list[str] = Field(min_length=1, description="Задачи стадии «Проектная документация»")
    rd_tasks: list[str] | None = Field(default=None, description="Задачи стадии «Рабочая документация»")
    surveys: SurveyWorkPackage
    construction_object: ConstructionObjectDraft

    @model_validator(mode="after")
    def _participant_exists(self) -> DesignAssignmentDraft:
        if self.developer is None and self.technical_customer is None:
            raise ValueError("Укажите застройщика и/или технического заказчика.")
        return self
