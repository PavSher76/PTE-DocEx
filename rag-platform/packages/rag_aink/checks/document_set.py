from rag_aink.context import ProjectCheckContext
from rag_aink.registry import register
from rag_aink.schemas import CheckResult, CheckStatus

# Минимальный ожидаемый набор дисциплин для ПД (настраивается в перспективе через БД).
EXPECTED_PD_DISCIPLINES = {"AR", "ST", "HV", "WS", "EL", "GP", "GEN"}
EXPECTED_DOC_MARKERS = ("пз", "пояснитель", "задание", "знп", "тз", "ведомость")


@register("document_set_completeness", "Проверка состава комплекта")
def check_document_set_completeness(ctx: ProjectCheckContext) -> CheckResult:
    if not ctx.documents:
        return CheckResult(
            check_id="document_set_completeness",
            title="Проверка состава комплекта",
            status=CheckStatus.FAILED,
            summary="В проекте нет загруженных документов.",
            recommendations=["Загрузите комплект ПД/РД через POST /documents/upload."],
        )

    indexed = ctx.indexed_documents
    not_indexed = [d for d in ctx.documents if not d.indexed]
    disciplines = ctx.disciplines
    missing_disciplines = EXPECTED_PD_DISCIPLINES - disciplines

    has_general = any(
        any(marker in (d.name or "").lower() or (d.document_code or "").lower() for marker in EXPECTED_DOC_MARKERS)
        for d in ctx.documents
    )

    details = [
        f"Документов в проекте: {len(ctx.documents)}, проиндексировано: {len(indexed)}.",
        f"Дисциплины в комплекте: {', '.join(sorted(disciplines)) or '—'}.",
    ]
    evidence = [{"document": d.name, "code": d.document_code, "indexed": d.indexed} for d in ctx.documents]

    status = CheckStatus.PASSED
    recommendations: list[str] = []

    if not_indexed:
        status = CheckStatus.WARNING
        details.append(f"Не проиндексировано: {len(not_indexed)} документ(ов).")
        recommendations.append("Дождитесь статуса indexed или перезапустите обработку.")

    if missing_disciplines and len(ctx.documents) >= 2:
        status = CheckStatus.WARNING if status != CheckStatus.FAILED else status
        details.append(f"Возможно отсутствуют разделы: {', '.join(sorted(missing_disciplines))}.")
        recommendations.append("Сверьте ведомость документов с фактически загруженными файлами.")

    if not has_general:
        status = CheckStatus.WARNING if status == CheckStatus.PASSED else status
        details.append("Не обнаружены ПЗ / Задание на проектирование / ведомость по наименованию.")
        recommendations.append("Добавьте пояснительную записку или задание на проектирование.")

    return CheckResult(
        check_id="document_set_completeness",
        title="Проверка состава комплекта",
        status=status,
        summary="Состав комплекта проверен по дисциплинам и статусу индексации.",
        details=details,
        evidence=evidence,
        recommendations=recommendations,
    )
