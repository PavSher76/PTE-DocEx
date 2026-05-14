import re
import subprocess
from difflib import SequenceMatcher, unified_diff
from pathlib import Path
from tempfile import TemporaryDirectory

from rapidfuzz import fuzz

from app.config import Settings
from app.schemas import PageComparison
from app.services.ocr import extract_pdf_pages


SUPPORTED_EDITABLE_EXTENSIONS = {".docx", ".odt", ".rtf"}


class DocumentComparisonService:
    def __init__(self, settings: Settings):
        self.settings = settings

    def compare(self, pdf_path: Path, editable_path: Path) -> tuple[float, list[PageComparison], str]:
        if pdf_path.suffix.lower() != ".pdf":
            raise ValueError("Первый файл должен быть PDF.")
        if editable_path.suffix.lower() not in SUPPORTED_EDITABLE_EXTENSIONS:
            raise ValueError("Редактируемый файл должен быть DOCX, ODT или RTF.")

        with TemporaryDirectory() as tmp:
            tmp_dir = Path(tmp)
            editable_pdf = self._convert_to_pdf(editable_path, tmp_dir)
            pdf_pages = self._extract_pages(pdf_path)
            editable_pages = self._extract_pages(editable_pdf)

        page_results = self._compare_pages(pdf_pages, editable_pages)
        similarity = self._overall_similarity(page_results)
        conclusion = self._build_conclusion(similarity, page_results)
        return similarity, page_results, conclusion

    def _convert_to_pdf(self, source: Path, output_dir: Path) -> Path:
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

    def _extract_pages(self, pdf_path: Path) -> list[str]:
        return [_normalize_text(page.text) for page in extract_pdf_pages(pdf_path, self.settings)]

    def _compare_pages(self, pdf_pages: list[str], editable_pages: list[str]) -> list[PageComparison]:
        max_pages = max(len(pdf_pages), len(editable_pages))
        results: list[PageComparison] = []
        for index in range(max_pages):
            pdf_text = pdf_pages[index] if index < len(pdf_pages) else ""
            editable_text = editable_pages[index] if index < len(editable_pages) else ""
            similarity = _text_similarity(pdf_text, editable_text)
            status = self._page_status(similarity)
            results.append(
                PageComparison(
                    page=index + 1,
                    similarity=round(similarity, 4),
                    status=status,
                    pdf_text=_preview(pdf_text),
                    editable_text=_preview(editable_text),
                    differences=_diff_preview(pdf_text, editable_text),
                )
            )
        return results

    def _page_status(self, similarity: float) -> str:
        if similarity >= self.settings.document_similarity_threshold:
            return "OK"
        if similarity >= self.settings.page_similarity_warning_threshold:
            return "Требует проверки"
        return "Критично"

    def _overall_similarity(self, page_results: list[PageComparison]) -> float:
        if not page_results:
            return 0.0
        return round(sum(page.similarity for page in page_results) / len(page_results), 4)

    def _build_conclusion(self, similarity: float, page_results: list[PageComparison]) -> str:
        critical_pages = [page.page for page in page_results if page.status == "Критично"]
        review_pages = [page.page for page in page_results if page.status == "Требует проверки"]

        if similarity >= self.settings.document_similarity_threshold and not critical_pages and not review_pages:
            return "Документы идентичны по результатам OCR-сравнения."
        if critical_pages:
            pages = ", ".join(str(page) for page in critical_pages)
            return f"Обнаружены существенные расхождения на страницах: {pages}."
        pages = ", ".join(str(page) for page in review_pages)
        return f"Документы близки, но требуют ручной проверки страниц: {pages}."


def _normalize_text(text: str) -> str:
    normalized = text.lower().replace("ё", "е")
    normalized = re.sub(r"[^\w\s.,;:!?%№/-]", " ", normalized, flags=re.UNICODE)
    return normalized.strip("\n")


def _text_similarity(left: str, right: str) -> float:
    if not left and not right:
        return 1.0
    token_score = fuzz.token_sort_ratio(left, right) / 100
    sequence_score = SequenceMatcher(None, left, right).ratio()
    return (token_score * 0.6) + (sequence_score * 0.4)


def _preview(text: str, limit: int = 1200) -> str:
    if len(text) <= limit:
        return text
    return f"{text[:limit]}..."


def _diff_preview(left: str, right: str, limit: int = 30) -> list[str]:
    left_lines = _split_for_diff(left)
    right_lines = _split_for_diff(right)
    diff = unified_diff(left_lines, right_lines, fromfile="pdf", tofile="editable", lineterm="")
    meaningful = [line for line in diff if line[:1] in {"+", "-"} and not line.startswith(("+++", "---"))]
    return meaningful[:limit]


def _split_for_diff(text: str, chunk_size: int = 120) -> list[str]:
    return [text[index : index + chunk_size] for index in range(0, len(text), chunk_size)] or [""]
