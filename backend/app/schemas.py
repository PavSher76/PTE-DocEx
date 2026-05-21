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


class RagIngestFileResult(BaseModel):
    filename: str
    document_id: str | None = None
    job_id: str | None = None
    error: str | None = None


class RagDeleteFileResult(BaseModel):
    document_id: str
    deleted: bool
    error: str | None = None


class RagDeleteSummary(BaseModel):
    enabled: bool = True
    documents_requested: int = 0
    documents_deleted: int = 0
    files: list[RagDeleteFileResult] = Field(default_factory=list)
    message: str = ""


class BundleDeleteResponse(BaseModel):
    batch_id: str
    local_deleted: bool = True
    rag: RagDeleteSummary | None = None


class RagIngestSummary(BaseModel):
    enabled: bool = True
    status: str = "skipped"
    project_id: str | None = None
    collection_label: str = "Анализ проекта"
    collection_name: str = "project_analysis_text"
    documents_queued: int = 0
    documents_failed: int = 0
    files: list[RagIngestFileResult] = Field(default_factory=list)
    message: str = ""
    last_error: str | None = None


class BundleStoredFile(BaseModel):
    original_filename: str
    size_bytes: int
    relative_path: str
    crc32_hex: str
    ukep: BundlePdfUkepValidation | None = None


class BundleListItem(BaseModel):
    batch_id: str
    project_cipher: str | None = None
    total_files: int
    created_at: datetime
    overall_ukep_status: Status
    pipeline_status: str
    pipeline_label: str
    rag_project_id: str | None = None


class BundlePipelineFileStatus(BaseModel):
    filename: str
    document_id: str | None = None
    job_status: str
    job_stage: str | None = None
    tokens_count: int = 0
    error: str | None = None


class BundleRagIngestInfo(BaseModel):
    enabled: bool = True
    status: str = ""
    project_id: str | None = None
    collection_label: str = "Анализ проекта"
    collection_name: str = "project_analysis_text"
    documents_queued: int = 0
    documents_failed: int = 0
    message: str = ""


class BundleDetailResponse(BaseModel):
    batch_id: str
    project_cipher: str | None = None
    total_files: int
    created_at: datetime
    overall_ukep_status: Status
    bundle_manifest_crc32_hex: str
    pipeline_status: str
    pipeline_label: str
    files: list[BundleStoredFile] = Field(default_factory=list)
    rag_ingest: BundleRagIngestInfo | None = None
    pipeline_files: list[BundlePipelineFileStatus] = Field(default_factory=list)


class DocumentBundleUploadResponse(BaseModel):
    """Результат пакетной загрузки комплекта документации (только PDF)."""

    batch_id: str
    project_cipher: str | None = Field(None, description="Шифр проекта, если указан при загрузке")
    total_files: int
    files: list[BundlePdfUploadItem]
    bundle_manifest_crc32_hex: str = Field(
        ...,
        description="CRC32 UTF-8 манифеста: строки path<TAB>crc32_hex по сортировке пути",
    )
    overall_ukep_status: Status
    ukep_disclaimer: str
    rag_ingest: RagIngestSummary | None = None


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


class BundleContextExcerpt(BaseModel):
    """Фрагмент текста из инженерного токена или результата поиска."""

    text: str
    source: Literal["token", "search"] = "token"
    document_id: str | None = None
    filename: str | None = None
    page_number: int | None = None
    element_type: str | None = None
    discipline: str | None = None
    document_code: str | None = None
    score: float | None = None


class BundleContextDocumentSummary(BaseModel):
    document_id: str
    filename: str
    job_status: str
    tokens_count: int = 0
    tokens_sampled: int = 0
    disciplines: list[str] = Field(default_factory=list)
    document_codes: list[str] = Field(default_factory=list)


class BundleContextStructured(BaseModel):
    batch_id: str
    project_cipher: str | None = None
    rag_project_id: str | None = None
    collection_label: str = "Анализ проекта"
    pipeline_status: str
    pipeline_label: str
    documents_indexed: int = 0
    documents_total: int = 0
    total_tokens: int = 0
    disciplines: list[str] = Field(default_factory=list)
    document_codes: list[str] = Field(default_factory=list)
    element_types: dict[str, int] = Field(default_factory=dict)
    documents: list[BundleContextDocumentSummary] = Field(default_factory=list)
    ntd_refs: list[str] = Field(default_factory=list)


class BundleProjectContextResponse(BaseModel):
    """Проектный контекст, собранный из проиндексированного комплекта PDF."""

    batch_id: str
    status: Literal["ready", "partial", "unavailable"]
    built_at: datetime
    summary: str
    structured: BundleContextStructured
    excerpts: list[BundleContextExcerpt] = Field(default_factory=list)
    ai_context_json: str = Field(
        ...,
        description="Компактный JSON для передачи в LLM (нарратив + структура + выдержки)",
    )
    message: str = ""


class IsmPackageListItem(BaseModel):
    package_id: str
    project_cipher: str | None = None
    title: str
    total_files: int
    documents_indexed: int = 0
    interfaces_count: int = 0
    created_at: datetime | str
    pipeline_status: str
    pipeline_label: str
    rag_project_id: str | None = None


class IsmDocumentItem(BaseModel):
    filename: str
    relative_path: str
    file_type: str
    size_bytes: int
    discipline: str | None = None
    document_codes: list[str] = Field(default_factory=list)
    section_hints: list[str] = Field(default_factory=list)
    excerpt: str = ""
    chars_extracted: int = 0
    parse_status: str = "ok"
    parse_error: str | None = None
    document_id: str | None = None
    rag_job_status: str | None = None
    tokens_count: int = 0
    rag_error: str | None = None


class IsmInterfaceItem(BaseModel):
    id: str
    source_filename: str
    target_filename: str | None = None
    target_discipline: str | None = None
    target_document_code: str | None = None
    reference_text: str
    link_type: str
    confidence: float


class IsmStructuredContext(BaseModel):
    collection_label: str = "Документы ИСМ"
    documents_total: int = 0
    disciplines: list[str] = Field(default_factory=list)
    document_codes: list[str] = Field(default_factory=list)
    interfaces_total: int = 0
    resolved_interfaces: int = 0


class IsmPackageDetailResponse(BaseModel):
    package_id: str
    project_cipher: str | None = None
    title: str
    created_at: datetime | str
    pipeline_status: str
    pipeline_label: str
    documents: list[IsmDocumentItem] = Field(default_factory=list)
    interfaces: list[IsmInterfaceItem] = Field(default_factory=list)
    structured_context: IsmStructuredContext
    rag_ingest: dict[str, Any] | None = None


class IsmPackageUploadResponse(BaseModel):
    package_id: str
    project_cipher: str | None = None
    title: str
    total_files: int
    pipeline_status: str
    pipeline_label: str
    documents: list[IsmDocumentItem]
    interfaces: list[IsmInterfaceItem]
    structured_context: IsmStructuredContext
    rag_ingest: dict[str, Any] | None = None


class ErrorResponse(BaseModel):
    detail: str | dict[str, Any]
