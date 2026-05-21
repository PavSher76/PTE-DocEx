from rag_aink.context import ProjectCheckContext
from rag_aink.registry import register
from rag_aink.schemas import CheckResult, CheckStatus


@register("stamp_quality", "Проверка штампов (качество OCR)")
def check_stamp_quality(ctx: ProjectCheckContext) -> CheckResult:
    stamps = [t for t in ctx.tokens if t.element_type == "stamp"]
    if not stamps:
        return CheckResult(
            check_id="stamp_quality",
            title="Проверка штампов (качество OCR)",
            status=CheckStatus.SKIPPED,
            summary="Штампы не извлечены — примените Sprint 3 к PDF-чертежам.",
        )

    bad = [t for t in stamps if t.quality in {"weak", "empty", "ocr_risk"}]
    status = CheckStatus.PASSED if not bad else CheckStatus.WARNING
    if len(bad) > len(stamps) / 2:
        status = CheckStatus.FAILED

    return CheckResult(
        check_id="stamp_quality",
        title="Проверка штампов (качество OCR)",
        status=status,
        summary=f"Штампов: {len(stamps)}, с риском OCR: {len(bad)}.",
        evidence=[
            {"page": t.page_number, "quality": t.quality, "text": (t.text or "")[:100]} for t in bad[:15]
        ],
        recommendations=["Пересканируйте листы или увеличьте DPI (DRAWING_RENDER_DPI)."],
    )
