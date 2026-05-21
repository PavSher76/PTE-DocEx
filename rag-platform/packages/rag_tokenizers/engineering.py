"""Инженерная токенизация Sprint 2: разделы, таблицы, требования, НТД, иерархия."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from uuid import UUID, uuid4

from rag_parsers.base import DocumentElementDTO
from rag_schemas.enums import ElementType, TokenQuality
from rag_tokenizers.metadata import (
    detect_discipline,
    detect_document_code,
    detect_revision,
    detect_stage,
    detect_status,
    extract_ntd_refs,
)

REQUIREMENT_PATTERNS = [
    r"\bдолжен\b",
    r"\bдолжна\b",
    r"\bдолжны\b",
    r"\bнеобходимо\b",
    r"\bтребуется\b",
    r"\bпредусмотреть\b",
    r"\bсогласно\b",
    r"\bв соответствии с\b",
]
REQUIREMENT_SPLIT = re.compile(r"(?<=[.;])\s+")
HEADING_NUMBERED = re.compile(r"^(\d+(?:\.\d+)*)\s+(.+)$")
TITLE_SHEET_HINTS = ("титул", "титульный лист", "обложка")
VOLUME_HINTS = ("состав тома", "содержание тома")
REGISTER_HINTS = ("ведомость документов", "ведомость чертежей", "ведомость")
CALC_HINTS = ("расчет", "расчёт", "расчеты", "расчёты")
SPEC_HINTS = ("спецификация", "спецификации")
DRAWING_HINTS = ("лист", "чертёж", "чертеж", "листов")


@dataclass
class TokenDraft:
    element_type: str
    text: str
    page_number: int | None
    bbox: list[float] | None
    quality: str
    ntd_refs: list[str]
    parent_index: int | None = None
    section_path: list[str] = field(default_factory=list)


class EngineeringTokenizer:
    def tokenize_elements(
        self,
        elements: list[DocumentElementDTO],
        *,
        project_id: str,
        document_id: UUID,
        version_id: UUID,
        source_uri: str,
        stage: str | None = None,
        discipline: str | None = None,
        document_code: str | None = None,
        revision: str | None = None,
        status: str | None = None,
    ) -> list[dict]:
        merged_text = "\n".join(e.text for e in elements if e.text)
        doc_code = document_code or detect_document_code(merged_text)
        doc_stage = stage or detect_stage(merged_text)
        doc_discipline = discipline or detect_discipline(doc_code, merged_text)
        doc_revision = revision or detect_revision(merged_text)
        doc_status = status or detect_status(merged_text)

        drafts = self._split_by_meaning(elements)
        tokens: list[dict] = []
        id_by_index: dict[int, UUID] = {}

        for index, draft in enumerate(drafts):
            token_id = uuid4()
            id_by_index[index] = token_id
            parent_id = (
                id_by_index.get(draft.parent_index) if draft.parent_index is not None else None
            )
            req_ids: list[str] = []
            if draft.element_type == ElementType.REQUIREMENT.value:
                req_ids.append(str(token_id))

            tokens.append(
                {
                    "id": token_id,
                    "project_id": project_id,
                    "document_id": document_id,
                    "version_id": version_id,
                    "stage": doc_stage,
                    "discipline": doc_discipline,
                    "document_code": doc_code,
                    "page_number": draft.page_number,
                    "element_type": draft.element_type,
                    "text": draft.text,
                    "bbox": draft.bbox,
                    "source_uri": source_uri,
                    "revision": doc_revision,
                    "status": doc_status,
                    "ntd_refs": draft.ntd_refs,
                    "requirement_refs": req_ids,
                    "parent_token_id": parent_id,
                    "quality": draft.quality,
                    "extra": {"section_path": draft.section_path},
                }
            )
        return tokens

    def _split_by_meaning(self, elements: list[DocumentElementDTO]) -> list[TokenDraft]:
        drafts: list[TokenDraft] = []
        section_stack: list[str] = []
        last_section_index: int | None = None

        for index, element in enumerate(elements):
            if element.table_markdown or element.element_type == ElementType.TABLE.value:
                drafts.append(
                    TokenDraft(
                        element_type=ElementType.TABLE.value,
                        text=element.table_markdown or element.text,
                        page_number=element.page_number,
                        bbox=element.bbox,
                        quality=self._quality(element, element.table_markdown or element.text),
                        ntd_refs=extract_ntd_refs(element.text),
                        parent_index=last_section_index,
                        section_path=list(section_stack),
                    )
                )
                continue

            for paragraph in self._paragraphs(element.text):
                classified = self._classify_paragraph(paragraph, element)
                if classified in {ElementType.SECTION.value, ElementType.SUBSECTION.value, ElementType.TITLE.value}:
                    section_stack = self._update_section_stack(section_stack, paragraph, classified)
                    last_section_index = len(drafts)

                for sentence in self._maybe_split_requirements(paragraph, classified):
                    element_type = classified
                    if self._is_requirement(sentence):
                        element_type = ElementType.REQUIREMENT.value

                    drafts.append(
                        TokenDraft(
                            element_type=element_type,
                            text=sentence,
                            page_number=element.page_number,
                            bbox=element.bbox,
                            quality=self._quality(element, sentence),
                            ntd_refs=extract_ntd_refs(sentence),
                            parent_index=last_section_index,
                            section_path=list(section_stack),
                        )
                    )
        return drafts

    def _paragraphs(self, text: str) -> list[str]:
        chunks = [chunk.strip() for chunk in re.split(r"\n{2,}", text) if chunk.strip()]
        return chunks or ([text.strip()] if text.strip() else [])

    def _classify_paragraph(self, text: str, element: DocumentElementDTO) -> str:
        lower = text.lower()
        if any(h in lower for h in TITLE_SHEET_HINTS):
            return ElementType.TITLE_SHEET.value
        if any(h in lower for h in VOLUME_HINTS):
            return ElementType.VOLUME_INDEX.value
        if any(h in lower for h in REGISTER_HINTS):
            return ElementType.DOCUMENT_REGISTER.value
        if any(h in lower for h in CALC_HINTS):
            return ElementType.CALCULATION.value
        if any(h in lower for h in SPEC_HINTS):
            return ElementType.SPECIFICATION.value
        if any(h in lower for h in DRAWING_HINTS) and len(text) < 80:
            return ElementType.DRAWING_SHEET.value
        if element.metadata.get("label") == "stamp" or "штамп" in lower:
            return ElementType.STAMP.value
        if self._looks_like_heading(text):
            if HEADING_NUMBERED.match(text.strip()):
                parts = text.strip().split()[0]
                if parts.count(".") >= 1:
                    return ElementType.SUBSECTION.value
            return ElementType.SECTION.value
        if element.element_type == "note" or text.startswith("Примечание"):
            return ElementType.NOTE.value
        return ElementType.TEXT.value

    def _update_section_stack(self, stack: list[str], title: str, kind: str) -> list[str]:
        if kind == ElementType.SECTION.value:
            return [title]
        if kind == ElementType.SUBSECTION.value:
            if not stack:
                return [title]
            return [stack[0], title]
        return stack

    def _maybe_split_requirements(self, paragraph: str, element_type: str) -> list[str]:
        if element_type == ElementType.REQUIREMENT.value or self._is_requirement(paragraph):
            parts = [p.strip() for p in REQUIREMENT_SPLIT.split(paragraph) if p.strip()]
            req_parts = [p for p in parts if self._is_requirement(p)]
            return req_parts or [paragraph]
        return [paragraph]

    def _is_requirement(self, text: str) -> bool:
        lower = text.lower()
        return any(re.search(pattern, lower) for pattern in REQUIREMENT_PATTERNS)

    def _looks_like_heading(self, text: str) -> bool:
        stripped = text.strip()
        if len(stripped) > 160:
            return False
        if HEADING_NUMBERED.match(stripped):
            return True
        return stripped.isupper() or stripped.endswith(":")

    def _quality(self, element: DocumentElementDTO, text: str) -> str:
        if not text.strip():
            return TokenQuality.EMPTY.value
        if element.metadata.get("ocr_risk"):
            return TokenQuality.OCR_RISK.value
        if len(text.strip()) < 12:
            return TokenQuality.WEAK.value
        garbled = sum(1 for ch in text if not ch.isalnum() and ch not in " .,;:-–—()[]/%«»\"'")
        if len(text) > 0 and garbled / len(text) > 0.35:
            return TokenQuality.OCR_RISK.value
        return TokenQuality.COMPLETE.value
