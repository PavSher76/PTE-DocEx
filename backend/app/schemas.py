from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field

Status = Literal["OK", "Требует проверки", "Критично"]


class HealthResponse(BaseModel):
    status: str
    app: str


class CorrespondenceRequest(BaseModel):
    text: str = Field(min_length=1, max_length=50000)
    terminology: list[str] = Field(default_factory=list)
    check_prompt: str | None = None
    business_context: str | None = None
    strictness: Literal["standard", "strict", "critical"] = "standard"


class LanguageIssue(BaseModel):
    message: str
    short_message: str | None = None
    offset: int | None = None
    length: int | None = None
    context: str | None = None
    rule_id: str | None = None
    category: str | None = None
    replacements: list[str] = Field(default_factory=list)
    severity: Literal["info", "warning", "critical"] = "warning"
    accepted: bool = True
    reason: str | None = None


class StyleAssessment(BaseModel):
    status: Status = "Требует проверки"
    tone: str = "Не оценено"
    ethics: str = "Не оценено"
    terminology: str = "Не оценено"
    recommendations: list[str] = Field(default_factory=list)


class CorrespondenceResponse(BaseModel):
    id: int
    status: Status
    source_text: str
    languagetool_report: dict[str, Any]
    ollama_prompt: str
    language_tool_matches: list[LanguageIssue]
    filtered_matches: list[LanguageIssue]
    style_assessment: StyleAssessment
    created_at: datetime


class PageComparison(BaseModel):
    page: int
    similarity: float
    status: Status
    pdf_text: str
    editable_text: str
    differences: list[str] = Field(default_factory=list)


class DocumentComparisonResponse(BaseModel):
    id: int
    status: Status
    similarity: float
    conclusion: str
    page_results: list[PageComparison]
    created_at: datetime


class Fz63CheckItem(BaseModel):
    id: str
    title: str
    passed: bool | None = None
    detail: str = ""


class BundlePdfUkepValidation(BaseModel):
    """Проверка встроенной УКЭП РФ, в т.ч. по 63-ФЗ."""

    sig_flags: int | None = Field(None, description="MuPDF/PyMuPDF get_sigflags, если доступен")
    signature_widget_count: int = 0
    has_signed_embedded_signature: bool = False
    signer_full_name: str | None = Field(None, description="ФИО подписанта (CN сертификата или /Name PDF)")
    certificate_valid: bool | None = Field(
        None,
        description="Срок действия сертификата на дату подписи (или сейчас)",
    )
    certificate_validity_label: str = Field(
        "не определено",
        description="Текст: действителен / истёк / ещё не действует / не определено",
    )
    signed_at: datetime | None = Field(None, description="Дата и время подписания (CMS signingTime или PDF /M)")
    is_qualified_certificate: bool | None = Field(None, description="Признаки квалифицированного сертификата 63-ФЗ")
    fz63_compliant: bool | None = Field(None, description="Итог проверки по 63-ФЗ")
    fz63_summary: str = ""
    fz63_checks: list[Fz63CheckItem] = Field(default_factory=list)
    status: Status
    message: str
    structural_validation_only: bool = True
    note: str = Field(..., description="Пояснение режима проверки")


class BundlePdfUploadItem(BaseModel):
    """Один файл из принятого комплекта PDF."""

    original_filename: str
    size_bytes: int
    relative_path: str
    crc32_hex: str = Field(..., description="CRC32 всего файла, 8 hex")
    ukep: BundlePdfUkepValidation


class DocumentBundleUploadResponse(BaseModel):
    """Результат пакетной загрузки комплекта документации (только PDF)."""

    batch_id: str
    total_files: int
    files: list[BundlePdfUploadItem]
    bundle_manifest_crc32_hex: str = Field(
        ...,
        description="CRC32 UTF-8 манифеста: строки path<TAB>crc32_hex по сортировке пути",
    )
    overall_ukep_status: Status
    ukep_disclaimer: str


class InvestmentProjectExportResponse(BaseModel):
    """Ответ: JSON для LLM и XML задания по схеме Минстроя."""

    ai_context_json: str
    design_assignment_xml: str


class LearnedLessonRootCause(BaseModel):
    title: str
    description: str
    related_lessons: list[str] = Field(default_factory=list)


class LearnedLessonsAnalysis(BaseModel):
    summary: str
    root_causes: list[LearnedLessonRootCause] = Field(default_factory=list)
    systemic_recommendations: list[str] = Field(default_factory=list)


class LearnedLessonsAnalyzeResponse(BaseModel):
    parsed_data: dict[str, Any]
    ollama_prompt: str
    ollama_model: str
    analysis: LearnedLessonsAnalysis
    status: Status


class OllamaModelsResponse(BaseModel):
    models: list[str]
    default_model: str
    ollama_reachable: bool = True
    error: str | None = None


class ErrorResponse(BaseModel):
    detail: str | dict[str, Any]
