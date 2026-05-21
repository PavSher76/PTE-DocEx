"""Разбор текста штампа: номер листа, ревизия, наименование."""

from __future__ import annotations

import re

SHEET_NUMBER_PATTERN = re.compile(
    r"(?:лист|л\.?)\s*[:№]?\s*(\d{1,3})|(?:^|\s)(\d{1,3})\s*(?:/|\s)\s*(\d{1,3})",
    re.IGNORECASE,
)
REVISION_IN_STAMP = re.compile(r"(?:рев|изм)\.?\s*[:№]?\s*([A-ZА-Я0-9]+)", re.IGNORECASE)
TITLE_LINE = re.compile(r"^([А-ЯЁA-Z0-9][\w\s\-\.«»]{4,80})$")


def parse_stamp_text(text: str) -> dict[str, str | None]:
    sheet_number = None
    sheet_total = None
    for match in SHEET_NUMBER_PATTERN.finditer(text):
        if match.group(1):
            sheet_number = match.group(1)
        if match.group(2) and match.group(3):
            sheet_number = match.group(2)
            sheet_total = match.group(3)
    revision = None
    rev_match = REVISION_IN_STAMP.search(text)
    if rev_match:
        revision = rev_match.group(1)
    title = None
    for line in text.splitlines():
        line = line.strip()
        if TITLE_LINE.match(line) and "лист" not in line.lower():
            title = line
            break
    return {
        "sheet_number": sheet_number,
        "sheet_total": sheet_total,
        "revision": revision,
        "sheet_title": title,
    }
