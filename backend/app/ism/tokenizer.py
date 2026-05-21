"""ISMDocumentTokenizer — process-aware токены для RAG (14 типов)."""

from __future__ import annotations

import re
import uuid
from dataclasses import dataclass

from app.ism.constants import ISM_TOKEN_TYPES
from app.ism.models import IsmDocument, IsmDocumentElement, IsmRagToken

_INPUT = re.compile(r"входн\w+\s+данн|исходн\w+\s+данн|input", re.I)
_OUTPUT = re.compile(r"выходн\w+\s+данн|результат|output|deliverable", re.I)
_RESP = re.compile(r"ответственн|исполнител|owner|владелец", re.I)
_CONTROL = re.compile(r"контрольн\w+\s+точк|КТ[-\s]?\d|checkpoint", re.I)
_RISK = re.compile(r"риск|опасност|hazard", re.I)
_KPI = re.compile(r"kpi|показател|метрик", re.I)
_LESSON = re.compile(r"урок|lesson\s+learned|ву\b", re.I)


@dataclass
class TokenDraft:
    token_type: str
    text: str
    section: str
    source_page: int | None
    source_table: str | None
    bbox: dict | list | None
    confidence: float


class ISMDocumentTokenizer:
    """Токенизация по логике процесса, не фиксированным чанкам."""

    ELEMENT_TO_TOKEN: dict[str, str] = {
        "process_step": "process_step",
        "requirement": "requirement",
        "responsibility": "responsibility",
        "input_data": "input_data",
        "output_data": "output_data",
        "checklist_item": "checklist_item",
        "form_field": "form_template",
        "reference": "document_reference",
        "section": "process_description",
        "subsection": "process_description",
        "title": "metadata",
        "metadata": "metadata",
        "paragraph": "process_description",
        "table": "form_template",
        "appendix": "document_reference",
    }

    def tokenize(self, document: IsmDocument, elements: list[IsmDocumentElement]) -> list[IsmRagToken]:
        drafts: list[TokenDraft] = []
        for el in elements:
            text = (el.text or "").strip()
            if len(text) < 10:
                continue
            token_type = self._resolve_token_type(el)
            drafts.append(
                TokenDraft(
                    token_type=token_type,
                    text=text[:4000],
                    section=el.section or "",
                    source_page=el.source_page,
                    source_table=el.source_table,
                    bbox=el.bbox,
                    confidence=0.93 if el.element_type != "paragraph" else 0.85,
                )
            )
        return [self._to_orm(document, d) for d in self._merge_adjacent(drafts)]

    def _resolve_token_type(self, el: IsmDocumentElement) -> str:
        mapped = self.ELEMENT_TO_TOKEN.get(el.element_type)
        if mapped and mapped in ISM_TOKEN_TYPES:
            base = mapped
        else:
            base = "process_description"
        text = el.text or ""
        if base == "process_description":
            if _INPUT.search(text):
                return "input_data"
            if _OUTPUT.search(text):
                return "output_data"
            if _RESP.search(text):
                return "responsibility"
            if _CONTROL.search(text):
                return "control_point"
            if _RISK.search(text):
                return "risk"
            if _KPI.search(text):
                return "kpi"
            if _LESSON.search(text):
                return "lesson_learned"
        return base

    def _merge_adjacent(self, drafts: list[TokenDraft]) -> list[TokenDraft]:
        if not drafts:
            return []
        merged: list[TokenDraft] = [drafts[0]]
        for d in drafts[1:]:
            prev = merged[-1]
            if (
                d.token_type == prev.token_type
                and d.section == prev.section
                and len(prev.text) + len(d.text) < 2800
            ):
                prev.text = f"{prev.text}\n{d.text}"
                prev.confidence = min(prev.confidence, d.confidence)
            else:
                merged.append(d)
        return merged

    def _to_orm(self, document: IsmDocument, draft: TokenDraft) -> IsmRagToken:
        return IsmRagToken(
            id=str(uuid.uuid4()),
            document_id=document.id,
            process_id=document.ism_process_id,
            document_code=document.code or "",
            document_type=document.document_type,
            revision=document.revision,
            section=draft.section,
            token_type=draft.token_type,
            text=draft.text,
            source_page=draft.source_page,
            source_table=draft.source_table,
            bbox=draft.bbox if isinstance(draft.bbox, dict) else None,
            confidence=draft.confidence,
        )


def tokenize_document(document: IsmDocument, elements: list[IsmDocumentElement]) -> list[IsmRagToken]:
    return ISMDocumentTokenizer().tokenize(document, elements)
