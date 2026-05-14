import re
from pathlib import Path

import pytesseract
from pdf2image import convert_from_path
from PIL import Image, ImageFilter, ImageOps
from pydantic import BaseModel
from pypdf import PdfReader

from app.config import Settings


class ExtractedPage(BaseModel):
    page: int
    text: str
    confidence: float
    source: str


def extract_pdf_pages(pdf_path: Path, settings: Settings) -> list[ExtractedPage]:
    if pdf_path.suffix.lower() != ".pdf":
        raise ValueError("Файл должен быть PDF.")

    if settings.ocr_use_text_layer:
        text_pages = _extract_text_layer(pdf_path, settings)
        if _has_enough_text(text_pages, settings):
            return text_pages

    return _extract_ocr_pages(pdf_path, settings)


def _extract_text_layer(pdf_path: Path, settings: Settings) -> list[ExtractedPage]:
    try:
        reader = PdfReader(str(pdf_path))
    except Exception:
        return []

    pages: list[ExtractedPage] = []
    for index, page in enumerate(reader.pages, start=1):
        try:
            text = page.extract_text() or ""
        except Exception:
            text = ""
        pages.append(
            ExtractedPage(
                page=index,
                text=_cleanup_text(text),
                confidence=100.0 if text.strip() else 0.0,
                source="pdf_text_layer",
            )
        )
    return pages


def _has_enough_text(pages: list[ExtractedPage], settings: Settings) -> bool:
    total_chars = sum(len(page.text.strip()) for page in pages)
    return total_chars >= settings.ocr_min_text_layer_chars


def _extract_ocr_pages(pdf_path: Path, settings: Settings) -> list[ExtractedPage]:
    try:
        images = convert_from_path(pdf_path, dpi=settings.ocr_dpi)
    except Exception as exc:
        raise RuntimeError(f"Не удалось прочитать PDF для OCR: {pdf_path.name}") from exc

    pages: list[ExtractedPage] = []
    psm_modes = _parse_psm_modes(settings.ocr_psm_modes)
    for index, image in enumerate(images, start=1):
        candidates = [
            _run_tesseract(candidate, settings, psm)
            for candidate in _image_candidates(image)
            for psm in psm_modes
        ]
        best_text, best_confidence = max(candidates, key=lambda item: _candidate_score(item[0], item[1]))
        if not best_text.strip():
            raise RuntimeError(f"Tesseract не смог распознать страницу {index} PDF: {pdf_path.name}")
        pages.append(
            ExtractedPage(
                page=index,
                text=_cleanup_text(best_text),
                confidence=round(best_confidence, 2),
                source="tesseract_ocr",
            )
        )
    return pages


def _image_candidates(image: Image.Image) -> list[Image.Image]:
    grayscale = ImageOps.grayscale(image)
    autocontrast = ImageOps.autocontrast(grayscale)
    sharpened = autocontrast.filter(ImageFilter.SHARPEN)
    thresholded = sharpened.point(lambda pixel: 255 if pixel > 180 else 0)
    return [image, autocontrast, sharpened, thresholded]


def _run_tesseract(image: Image.Image, settings: Settings, psm: int) -> tuple[str, float]:
    config = f"--oem 1 --psm {psm} -c preserve_interword_spaces=1"
    try:
        data = pytesseract.image_to_data(
            image,
            lang=settings.ocr_language,
            config=config,
            output_type=pytesseract.Output.DICT,
        )
    except Exception as exc:
        raise RuntimeError("Tesseract не смог выполнить OCR.") from exc

    lines: dict[tuple[int, int, int], list[str]] = {}
    confidences: list[float] = []
    for index, raw_text in enumerate(data.get("text", [])):
        word = str(raw_text).strip()
        if not word:
            continue
        confidence = _parse_confidence(data.get("conf", ["-1"])[index])
        if confidence >= 0:
            confidences.append(confidence)
        key = (
            int(data.get("block_num", [0])[index]),
            int(data.get("par_num", [0])[index]),
            int(data.get("line_num", [0])[index]),
        )
        lines.setdefault(key, []).append(word)

    text = "\n".join(" ".join(words) for _, words in sorted(lines.items()))
    if not text.strip():
        text = pytesseract.image_to_string(image, lang=settings.ocr_language, config=config)

    confidence = sum(confidences) / len(confidences) if confidences else 0.0
    return text, confidence


def _candidate_score(text: str, confidence: float) -> float:
    normalized_len = min(len(_cleanup_text(text)) / 2000, 1.0)
    return confidence + (normalized_len * 10)


def _parse_confidence(value: object) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return -1.0


def _parse_psm_modes(raw_value: str) -> list[int]:
    modes: list[int] = []
    for item in raw_value.split(","):
        try:
            mode = int(item.strip())
        except ValueError:
            continue
        if mode not in modes:
            modes.append(mode)
    return modes or [3]


def _cleanup_text(text: str) -> str:
    text = text.replace("\x0c", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r" *\n *", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()
