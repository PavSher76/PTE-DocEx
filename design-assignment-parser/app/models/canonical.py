"""Каноническая модель: PDF/OCR → canonical JSON → XML (не напрямую PDF→XML)."""

from __future__ import annotations

from datetime import date
from typing import Any, Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class TraceabilityEntry(BaseModel):
    canonical_path: str
    xml_path: str | None = None
    page_number: int | None = None
    bbox: list[float] | None = None
    source_text: str | None = None
    confidence: float = 0.0
    extraction_method: str = "heuristic"
    corrected: bool = False
    original_value: Any | None = None
    corrected_value: Any | None = None
    corrected_by: str | None = None
    correction_reason: str | None = None


class DocumentMeta(BaseModel):
    document_id: str | None = None
    document_type_code: str | None = "05.03"
    version_number: int | None = 1
    schema_version: str | None = "01.00"
    schema_url: str | None = None
    document_date: date | None = None
    approval_date: date | None = None
    document_number: str | None = None


class OrganizationBlock(BaseModel):
    full_name: str | None = None
    abbreviated_name: str | None = None
    ogrn: str | None = None
    inn: str | None = None
    kpp: str | None = None
    address_note: str | None = None


class PersonBlock(BaseModel):
    surname: str | None = None
    name: str | None = None
    patronymic: str | None = None
    position: str | None = None


class ParticipantsBlock(BaseModel):
    developer: OrganizationBlock = Field(default_factory=OrganizationBlock)
    technical_customer: OrganizationBlock = Field(default_factory=OrganizationBlock)
    designer: OrganizationBlock = Field(default_factory=OrganizationBlock)
    author: OrganizationBlock = Field(default_factory=OrganizationBlock)
    signer: PersonBlock = Field(default_factory=PersonBlock)


class ObjectBlock(BaseModel):
    name: str | None = None
    code: str | None = None
    address: str | None = None
    address_note: str | None = None
    cadastre_numbers: list[str] = Field(default_factory=list)
    construction_type: str | None = None
    functional_purpose: str | None = None
    region_code: str | None = None


class RequirementRecord(BaseModel):
    requirement_id: str
    type: Literal[
        "customer_requirement",
        "ntd_requirement",
        "source_data_requirement",
        "engineering_survey_requirement",
        "design_scope_requirement",
        "operation_requirement",
        "digital_requirement",
        "safety_requirement",
        "other",
    ] = "other"
    text: str
    normalized_text: str | None = None
    source_page: int | None = None
    bbox: list[float] | None = None
    confidence: float = 0.0
    canonical_path: str | None = None
    xml_path: str | None = None


class DesignRequirementsBlock(BaseModel):
    stage: str | None = None
    composition: list[str] = Field(default_factory=list)
    technical_requirements: list[str] = Field(default_factory=list)
    source_data: list[str] = Field(default_factory=list)
    engineering_surveys: list[str] = Field(default_factory=list)
    ntd_requirements: list[str] = Field(default_factory=list)
    operation_requirements: list[str] = Field(default_factory=list)
    objective_text: list[str] = Field(default_factory=list)
    digital_requirements: list[str] = Field(default_factory=list)
    cost_requirements: list[str] = Field(default_factory=list)
    appendices: list[str] = Field(default_factory=list)


class DesignAssignmentCanonical(BaseModel):
    document: DocumentMeta = Field(default_factory=DocumentMeta)
    participants: ParticipantsBlock = Field(default_factory=ParticipantsBlock)
    object: ObjectBlock = Field(default_factory=ObjectBlock)
    design_requirements: DesignRequirementsBlock = Field(default_factory=DesignRequirementsBlock)
    requirements: list[RequirementRecord] = Field(default_factory=list)
    traceability: list[TraceabilityEntry] = Field(default_factory=list)

    def ensure_document_id(self) -> None:
        if not self.document.document_id:
            self.document.document_id = str(uuid4())

    def add_trace(
        self,
        canonical_path: str,
        value: Any,
        *,
        page: int | None = None,
        bbox: list[float] | None = None,
        confidence: float = 0.0,
        method: str = "heuristic",
        xml_path: str | None = None,
    ) -> None:
        self.traceability.append(
            TraceabilityEntry(
                canonical_path=canonical_path,
                xml_path=xml_path,
                page_number=page,
                bbox=bbox,
                source_text=str(value) if value is not None else None,
                confidence=confidence,
                extraction_method=method,
            )
        )
