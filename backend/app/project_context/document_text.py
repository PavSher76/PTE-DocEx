"""Извлечение текста из загруженных документов для обогащения контекста проекта."""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

from app.config import Settings
from app.services.document_compare import SUPPORTED_EDITABLE_EXTENSIONS
from app.services.ocr import extract_pdf_pages
from app.services.pdf_text import extract_pdf_text

_TEXT_EXTENSIONS = {".txt", ".md"}


def extract_document_text(path: Path, settings: Settings) -> str:
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return extract_pdf_text(path, settings).text.strip()
    if suffix in _TEXT_EXTENSIONS:
        return path.read_text(encoding="utf-8", errors="replace").strip()
    if suffix in SUPPORTED_EDITABLE_EXTENSIONS:
        return _extract_editable_document_text(path, settings)
    raise ValueError("Поддерживаются PDF, TXT, MD, DOCX, ODT и RTF.")


def _extract_editable_document_text(source: Path, settings: Settings) -> str:
    with TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        pdf_path = _convert_to_pdf(source, tmp_dir)
        pages = extract_pdf_pages(pdf_path, settings)
    text = "\n\n".join(page.text for page in pages if page.text.strip())
    if not text.strip():
        raise ValueError("Не удалось извлечь текст из документа. Проверьте LibreOffice и качество файла.")
    return text.strip()


def _convert_to_pdf(source: Path, output_dir: Path) -> Path:
    import subprocess

    command = [
        "libreoffice",
        "--headless",
        "--convert-to",
        "pdf",
        "--outdir",
        str(output_dir),
        str(source),
    ]
    try:
        completed = subprocess.run(command, check=False, capture_output=True, text=True, timeout=120)
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError("LibreOffice не успел конвертировать файл за 120 секунд.") from exc
    if completed.returncode != 0:
        raise RuntimeError(f"LibreOffice не смог конвертировать файл: {completed.stderr}")

    converted = output_dir / f"{source.stem}.pdf"
    if not converted.exists():
        candidates = list(output_dir.glob("*.pdf"))
        if not candidates:
            raise RuntimeError("LibreOffice не создал PDF-файл.")
        converted = candidates[0]
    return converted
