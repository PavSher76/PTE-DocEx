from rag_aink.context import ProjectCheckContext
from rag_aink.registry import register
from rag_aink.schemas import CheckResult, CheckStatus


@register("title_block_completeness", "Проверка титульных листов и штампов")
def check_title_block_completeness(ctx: ProjectCheckContext) -> CheckResult:
    drawing_pages = [p for p in ctx.pages if p.image_uri]
    stamp_tokens = [t for t in ctx.tokens if t.element_type == "stamp"]
    title_tokens = [t for t in ctx.tokens if t.element_type in {"title", "title_sheet"}]

    if not drawing_pages and not stamp_tokens:
        return CheckResult(
            check_id="title_block_completeness",
            title="Проверка титульных листов и штампов",
            status=CheckStatus.SKIPPED,
            summary="Нет листов чертежей (Sprint 3) — проверка пропущена.",
        )

    incomplete_stamps = [
        t
        for t in stamp_tokens
        if not (t.text or "").strip() or t.quality in {"weak", "empty", "ocr_risk"}
    ]
    pages_without_sheet = [
        p.page_number
        for p in drawing_pages
        if p.page_number not in {t.page_number for t in stamp_tokens if t.sheet_number}
    ]

    status = CheckStatus.PASSED
    if incomplete_stamps or pages_without_sheet:
        status = CheckStatus.WARNING if not incomplete_stamps else CheckStatus.FAILED

    return CheckResult(
        check_id="title_block_completeness",
        title="Проверка титульных листов и штампов",
        status=status,
        summary=f"Листов с изображением: {len(drawing_pages)}, штампов: {len(stamp_tokens)}, титулов: {len(title_tokens)}.",
        details=[
            f"Штампов с низким качеством OCR: {len(incomplete_stamps)}.",
            f"Листов без номера в штампе: {len(pages_without_sheet)}.",
        ],
        evidence=[
            {"page": t.page_number, "sheet": t.sheet_number, "quality": t.quality, "preview": t.text[:120]}
            for t in stamp_tokens[:20]
        ],
        recommendations=[
            "Проверьте читаемость штампа на листах с ocr_risk.",
            "Уточните номера листов в основной надписи.",
        ]
        if pages_without_sheet
        else [],
    )
