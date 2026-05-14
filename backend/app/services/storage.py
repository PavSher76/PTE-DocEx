from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile

from app.config import Settings


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
