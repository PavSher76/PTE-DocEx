from pathlib import Path

from rag_parsers.base import DocumentElementDTO, ParserAdapter


class PypdfParserAdapter(ParserAdapter):
    name = "pypdf"

    def parse(self, path: Path, file_type: str) -> list[DocumentElementDTO]:
        if file_type != "pdf":
            raise ValueError("pypdf поддерживает только PDF")
        from pypdf import PdfReader

        reader = PdfReader(str(path))
        elements: list[DocumentElementDTO] = []
        for index, page in enumerate(reader.pages, start=1):
            text = (page.extract_text() or "").strip()
            if not text:
                continue
            elements.append(
                DocumentElementDTO(
                    page_number=index,
                    element_type="text",
                    text=text,
                    reading_order=index,
                    metadata={"parser": self.name, "ocr_risk": len(text) < 40},
                )
            )
        return elements
