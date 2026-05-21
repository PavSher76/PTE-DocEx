from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class RenderedPage:
    page_number: int
    width: int
    height: int
    png_bytes: bytes
    is_likely_drawing: bool
    text_char_count: int


def render_pdf_pages(path: Path, *, dpi: int = 200) -> list[RenderedPage]:
    try:
        import fitz  # PyMuPDF
    except ImportError as exc:
        raise RuntimeError("PyMuPDF не установлен: pip install 'rag-platform[drawings]'") from exc

    document = fitz.open(str(path))
    pages: list[RenderedPage] = []
    try:
        for index in range(document.page_count):
            page = document[index]
            text = (page.get_text("text") or "").strip()
            pixmap = page.get_pixmap(dpi=dpi, alpha=False)
            png_bytes = pixmap.tobytes("png")
            width, height = pixmap.width, pixmap.height
            is_drawing = _is_likely_drawing_page(len(text), width, height)
            pages.append(
                RenderedPage(
                    page_number=index + 1,
                    width=width,
                    height=height,
                    png_bytes=png_bytes,
                    is_likely_drawing=is_drawing,
                    text_char_count=len(text),
                )
            )
    finally:
        document.close()
    return pages


def _is_likely_drawing_page(text_chars: int, width: int, height: int) -> bool:
    if width < 800 or height < 600:
        return False
    aspect = width / max(height, 1)
    landscape_a_series = 1.2 <= aspect <= 1.8
    portrait_a_series = 0.65 <= aspect <= 0.85
    low_text = text_chars < 280
    return (landscape_a_series or portrait_a_series) and low_text
