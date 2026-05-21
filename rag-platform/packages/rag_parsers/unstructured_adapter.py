"""Fallback: Unstructured hi_res для сложных PDF."""

from __future__ import annotations

from pathlib import Path

from rag_parsers.base import DocumentElementDTO, ParserAdapter

_CATEGORY_MAP = {
    "Title": "title",
    "Header": "title",
    "NarrativeText": "text",
    "Text": "text",
    "ListItem": "text",
    "Table": "table",
    "Footer": "note",
    "FigureCaption": "note",
}


class UnstructuredParserAdapter(ParserAdapter):
    name = "unstructured"

    def parse(self, path: Path, file_type: str) -> list[DocumentElementDTO]:
        try:
            from unstructured.partition.auto import partition
        except ImportError as exc:
            raise RuntimeError(
                "Unstructured не установлен: pip install 'rag-platform[parsers]'"
            ) from exc

        strategy = "hi_res" if file_type == "pdf" else "auto"
        raw_elements = partition(filename=str(path), strategy=strategy, languages=["rus", "eng"])
        elements: list[DocumentElementDTO] = []
        for order, item in enumerate(raw_elements, start=1):
            text = (getattr(item, "text", None) or "").strip()
            if not text:
                continue
            category = getattr(item, "category", "Text")
            element_type = _CATEGORY_MAP.get(str(category), "text")
            page_number = getattr(item.metadata, "page_number", None) if hasattr(item, "metadata") else None
            bbox = None
            if hasattr(item, "metadata") and getattr(item.metadata, "coordinates", None):
                coords = item.metadata.coordinates
                if hasattr(coords, "points"):
                    xs = [p[0] for p in coords.points]
                    ys = [p[1] for p in coords.points]
                    bbox = [min(xs), min(ys), max(xs), max(ys)]
            table_markdown = text if element_type == "table" else None
            elements.append(
                DocumentElementDTO(
                    page_number=int(page_number or 1),
                    element_type=element_type,
                    text=text,
                    bbox=bbox,
                    reading_order=order,
                    table_markdown=table_markdown,
                    metadata={"parser": self.name, "category": str(category)},
                )
            )
        return elements
