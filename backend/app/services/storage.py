from pathlib import Path
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
    destination = unique_path_in_dir(batch_dir, _safe_filename(filename))
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
    destination = destination_dir / _safe_filename(filename)

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


def _safe_filename(filename: str) -> str:
    allowed = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-")
    cleaned = "".join(char if char in allowed else "_" for char in Path(filename).name)
    return cleaned or "upload.bin"
