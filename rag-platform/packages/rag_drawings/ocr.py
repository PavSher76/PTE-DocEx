from __future__ import annotations

from dataclasses import dataclass

from rag_drawings.zones import SheetZone


@dataclass
class ZoneOcrResult:
    zone: SheetZone
    text: str
    bbox: list[float]
    confidence: float
    ocr_available: bool


def ocr_zone(png_bytes: bytes, zone: SheetZone, *, lang: str = "rus+eng") -> ZoneOcrResult:
    from PIL import Image

    image = Image.open(__import__("io").BytesIO(png_bytes)).convert("RGB")
    width, height = image.size
    left, top, right, bottom = zone.to_pixels(width, height)
    if right <= left or bottom <= top:
        return ZoneOcrResult(zone=zone, text="", bbox=zone.bbox_list(width, height), confidence=0.0, ocr_available=False)

    crop = image.crop((left, top, right, bottom))
    bbox = zone.bbox_list(width, height)

    try:
        import pytesseract
    except ImportError:
        return ZoneOcrResult(zone=zone, text="", bbox=bbox, confidence=0.0, ocr_available=False)

    try:
        text = pytesseract.image_to_string(crop, lang=lang).strip()
        data = pytesseract.image_to_data(crop, lang=lang, output_type=pytesseract.Output.DICT)
        confidences = [float(c) for c in data.get("conf", []) if str(c) not in {"", "-1"}]
        confidence = sum(confidences) / len(confidences) / 100.0 if confidences else 0.5
    except Exception:
        return ZoneOcrResult(zone=zone, text="", bbox=bbox, confidence=0.0, ocr_available=False)

    return ZoneOcrResult(zone=zone, text=text, bbox=bbox, confidence=confidence, ocr_available=True)
