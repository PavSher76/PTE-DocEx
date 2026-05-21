"""Основной парсер: Docling (PDF, DOCX, PPTX, изображения)."""

from __future__ import annotations

from pathlib import Path

from rag_parsers.base import DocumentElementDTO, ParserAdapter

_DOCLING_LABEL_MAP = {
    "title": "title",
    "section_header": "title",
    "paragraph": "text",
    "text": "text",
    "table": "table",
    "list_item": "text",
    "caption": "note",
    "footnote": "note",
    "page_header": "note",
    "page_footer": "note",
}


class DoclingParserAdapter(ParserAdapter):
    name = "docling"

    def parse(self, path: Path, file_type: str) -> list[DocumentElementDTO]:
        try:
            from docling.document_converter import DocumentConverter
        except ImportError as exc:
            raise RuntimeError(
                "Docling не установлен: pip install 'rag-platform[parsers]'"
            ) from exc

        converter = DocumentConverter()
        result = converter.convert(str(path))
        document = result.document
        elements: list[DocumentElementDTO] = []
        order = 0

        if hasattr(document, "iterate_items"):
            for item, _level in document.iterate_items():
                order += 1
                dto = self._item_to_dto(item, order)
                if dto:
                    elements.append(dto)
        else:
            text = document.export_to_markdown()
            elements.extend(self._markdown_blocks(text))

        if not elements:
            text = document.export_to_markdown() if hasattr(document, "export_to_markdown") else ""
            if text.strip():
                elements.append(
                    DocumentElementDTO(
                        page_number=1,
                        element_type="text",
                        text=text.strip(),
                        reading_order=1,
                        metadata={"parser": self.name},
                    )
                )
        return elements

    def _item_to_dto(self, item: object, order: int) -> DocumentElementDTO | None:
        label = str(getattr(item, "label", "text")).lower().replace("itemlabel.", "")
        element_type = _DOCLING_LABEL_MAP.get(label, "text")
        text = (getattr(item, "text", None) or "").strip()
        if not text and hasattr(item, "export_to_markdown"):
            text = (item.export_to_markdown() or "").strip()  # type: ignore[union-attr]
        if not text:
            return None

        page_number = 1
        prov = getattr(item, "prov", None)
        if prov and len(prov) > 0:
            page_number = int(getattr(prov[0], "page_no", 1) or 1)

        bbox = None
        if prov and len(prov) > 0 and getattr(prov[0], "bbox", None):
            box = prov[0].bbox
            bbox = [
                float(getattr(box, "l", 0)),
                float(getattr(box, "t", 0)),
                float(getattr(box, "r", 0)),
                float(getattr(box, "b", 0)),
            ]

        table_markdown = None
        if element_type == "table" and hasattr(item, "export_to_dataframe"):
            try:
                df = item.export_to_dataframe()  # type: ignore[union-attr]
                table_markdown = df.to_markdown(index=False)
            except Exception:
                table_markdown = text

        return DocumentElementDTO(
            page_number=page_number,
            element_type=element_type,
            text=text,
            bbox=bbox,
            reading_order=order,
            table_markdown=table_markdown,
            metadata={"parser": self.name, "label": label},
        )

    def _markdown_blocks(self, markdown: str) -> list[DocumentElementDTO]:
        blocks: list[DocumentElementDTO] = []
        order = 0
        for raw in markdown.split("\n\n"):
            block = raw.strip()
            if not block:
                continue
            order += 1
            element_type = "table" if block.startswith("|") else "text"
            if block.startswith("#"):
                element_type = "title"
            blocks.append(
                DocumentElementDTO(
                    page_number=1,
                    element_type=element_type,
                    text=block,
                    reading_order=order,
                    table_markdown=block if element_type == "table" else None,
                    metadata={"parser": self.name, "from": "markdown"},
                )
            )
        return blocks
