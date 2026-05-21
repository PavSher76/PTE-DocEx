from pathlib import Path
import re
import unicodedata
from uuid import uuid4

from fastapi import HTTPException, UploadFile

from app.config import Settings


def unique_path_in_dir(directory: Path, filename: str) -> Path:
    """Возвращает путь вида directory/filename, при коллизии добавляет _2, _3, …"""
    base = Path(filename).name
    candidate = directory / base
    if not candidate.exists():
        return candidate
    stem = candidate.stem
    suffix = candidate.suffix
    counter = 2
    while True:
        alt = directory / f"{stem}_{counter}{suffix}"
        if not alt.exists():
            return alt
        counter += 1


async def save_bundle_pdf(upload: UploadFile, settings: Settings, batch_dir: Path) -> tuple[Path, int]:
    """Сохраняет один PDF в каталог комплекта; возвращает путь и размер в байтах."""
    filename = upload.filename or "document.pdf"
    destination = unique_path_in_dir(batch_dir, safe_filename(filename))
    max_bytes = settings.max_upload_mb * 1024 * 1024
    total = 0
    with destination.open("wb") as target:
        while chunk := await upload.read(1024 * 1024):
            total += len(chunk)
            if total > max_bytes:
                destination.unlink(missing_ok=True)
                raise HTTPException(status_code=413, detail=f"Файл больше {settings.max_upload_mb} МБ")
            target.write(chunk)
    return destination, total


async def save_upload(upload: UploadFile, settings: Settings, subdir: str) -> Path:
    filename = upload.filename or "upload.bin"
    destination_dir = settings.storage_dir / subdir / uuid4().hex
    destination_dir.mkdir(parents=True, exist_ok=True)
    destination = destination_dir / safe_filename(filename)

    max_bytes = settings.max_upload_mb * 1024 * 1024
    total = 0
    with destination.open("wb") as target:
        while chunk := await upload.read(1024 * 1024):
            total += len(chunk)
            if total > max_bytes:
                destination.unlink(missing_ok=True)
                raise HTTPException(status_code=413, detail=f"Файл больше {settings.max_upload_mb} МБ")
            target.write(chunk)

    return destination


def safe_filename(filename: str) -> str:
    """Безопасное имя файла с сохранением кириллицы (в отличие от ASCII-only sanitization)."""
    name = Path(filename).name
    name = unicodedata.normalize("NFC", name)
    # Запрещены разделители пути и управляющие символы
    name = re.sub(r"[/\\:\x00-\x1f]", "_", name)
    name = name.strip().strip(".")
    if not name or name in {".", ".."}:
        return "upload.bin"
    if len(name) > 240:
        path = Path(name)
        stem, suffix = path.stem, path.suffix
        max_stem = 240 - len(suffix)
        name = (stem[:max_stem] if max_stem > 0 else "file") + suffix
    return name


# Обратная совместимость для внутренних вызовов
_safe_filename = safe_filename
