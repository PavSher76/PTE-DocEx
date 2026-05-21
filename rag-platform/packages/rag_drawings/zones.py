"""Зоны листа чертежа (ГОСТ: штамп справа снизу, примечания, спецификация)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SheetZone:
    name: str
    element_type: str
    x0: float
    y0: float
    x1: float
    y1: float

    def to_pixels(self, width: int, height: int) -> tuple[int, int, int, int]:
        left = max(0, int(self.x0 * width))
        top = max(0, int(self.y0 * height))
        right = min(width, int(self.x1 * width))
        bottom = min(height, int(self.y1 * height))
        return left, top, right, bottom

    def bbox_list(self, width: int, height: int) -> list[float]:
        left, top, right, bottom = self.to_pixels(width, height)
        return [float(left), float(top), float(right), float(bottom)]


# Нормализованные координаты (0..1), начало — левый верхний угол.
DEFAULT_DRAWING_ZONES: list[SheetZone] = [
    SheetZone("stamp", "stamp", 0.62, 0.78, 1.0, 1.0),
    SheetZone("sheet_title", "title", 0.62, 0.72, 1.0, 0.78),
    SheetZone("notes", "note", 0.0, 0.0, 0.28, 0.35),
    SheetZone("specification", "specification", 0.0, 0.72, 0.62, 0.78),
    SheetZone("main_drawing", "drawing_zone", 0.05, 0.05, 0.95, 0.72),
]

A_SERIES_MM = {
    "A0": (841, 1189),
    "A1": (594, 841),
    "A2": (420, 594),
    "A3": (297, 420),
    "A4": (210, 297),
}


def detect_sheet_format(width_px: int, height_px: int, dpi: int) -> str | None:
    """Определяет формат листа по размеру рендера и DPI."""
    width_mm = width_px / dpi * 25.4
    height_mm = height_px / dpi * 25.4
    long_side = max(width_mm, height_mm)
    short_side = min(width_mm, height_mm)
    best: str | None = None
    best_delta = float("inf")
    for name, (w_mm, h_mm) in A_SERIES_MM.items():
        for pair in ((w_mm, h_mm), (h_mm, w_mm)):
            delta = abs(pair[0] - short_side) + abs(pair[1] - long_side)
            if delta < best_delta:
                best_delta = delta
                best = name
    if best_delta > 80:
        return None
    return best
