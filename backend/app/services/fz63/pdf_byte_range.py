"""Хеш содержимого PDF по ByteRange для встроенной подписи."""

from __future__ import annotations

from pathlib import Path


def hash_pdf_byte_range(pdf_path: Path, byte_range: list[int]) -> bytes | None:
    """Возвращает объединённые байты диапазонов ByteRange или None при ошибке."""
    if len(byte_range) < 4 or len(byte_range) % 2 != 0:
        return None
    chunks: list[bytes] = []
    try:
        with pdf_path.open("rb") as handle:
            for i in range(0, len(byte_range), 2):
                start = int(byte_range[i])
                length = int(byte_range[i + 1])
                handle.seek(start)
                part = handle.read(length)
                if len(part) != length:
                    return None
                chunks.append(part)
    except OSError:
        return None
    return b"".join(chunks)
