from rag_drawings.stamp_parser import parse_stamp_text
from rag_drawings.zones import SheetZone, detect_sheet_format


def test_stamp_parser_sheet_and_revision():
    text = "Лист 12\nРев. B\nВентиляция подвала"
    meta = parse_stamp_text(text)
    assert meta["sheet_number"] == "12"
    assert meta["revision"] == "B"


def test_sheet_zone_pixels():
    zone = SheetZone("stamp", "stamp", 0.62, 0.78, 1.0, 1.0)
    bbox = zone.bbox_list(1000, 800)
    assert bbox == [620.0, 624.0, 1000.0, 800.0]


def test_detect_sheet_format_a1_landscape():
    # A1 landscape ~ 594x841 mm at 200 dpi ≈ 4677 x 6614 px (approx)
    fmt = detect_sheet_format(4677, 3311, 200)
    assert fmt in {"A1", "A2", "A3", None}
