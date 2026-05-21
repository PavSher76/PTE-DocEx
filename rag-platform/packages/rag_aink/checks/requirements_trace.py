import re

from rag_aink.context import ProjectCheckContext
from rag_aink.registry import register
from rag_aink.schemas import CheckResult, CheckStatus

IMPLEMENTATION_HINTS = re.compile(
    r"\b(предусмотр|выполнить|монтаж|прокладк|установ|смонтир|оборудован)",
    re.IGNORECASE,
)


@register("requirements_traceability", "Трассировка требований")
def check_requirements_traceability(ctx: ProjectCheckContext) -> CheckResult:
    if not ctx.requirements:
        req_tokens = [t for t in ctx.tokens if t.element_type == "requirement"]
        if not req_tokens:
            return CheckResult(
                check_id="requirements_traceability",
                title="Трассировка требований",
                status=CheckStatus.SKIPPED,
                summary="Требования не извлечены — загрузите ТЗ/ПЗ или документы с формулировками «должен».",
            )
        return CheckResult(
            check_id="requirements_traceability",
            title="Трассировка требований",
            status=CheckStatus.WARNING,
            summary=f"Найдено {len(req_tokens)} requirement-токенов, но нет записей в реестре Requirement.",
            recommendations=["Переиндексируйте документы после Sprint 2."],
        )

    untraced: list[dict] = []
    traced = 0
    for req in ctx.requirements:
        keywords = {w.lower() for w in req.text.split() if len(w) > 5}
        if len(keywords) > 12:
            keywords = set(list(keywords)[:12])
        evidence_tokens = []
        for token in ctx.tokens:
            if token.element_type == "requirement" and token.text == req.text:
                continue
            overlap = keywords & {w.lower() for w in token.text.split() if len(w) > 5}
            if overlap and (IMPLEMENTATION_HINTS.search(token.text) or token.element_type != "requirement"):
                evidence_tokens.append(token)
        if evidence_tokens:
            traced += 1
        else:
            untraced.append({"requirement_id": str(req.id), "status": req.status, "text": req.text[:180]})

    ratio = traced / len(ctx.requirements) if ctx.requirements else 0
    status = CheckStatus.PASSED if ratio >= 0.5 else CheckStatus.WARNING
    if ratio < 0.2:
        status = CheckStatus.FAILED

    return CheckResult(
        check_id="requirements_traceability",
        title="Трассировка требований",
        status=status,
        summary=f"Требований: {len(ctx.requirements)}, с признаками реализации: {traced} ({ratio:.0%}).",
        details=[f"Без подтверждения в комплекте: {len(untraced)}."],
        evidence=untraced[:15],
        recommendations=[
            "Сопоставьте требования Заказчика с разделами ПД/РД.",
            "Используйте POST /requirements/{{id}}/trace для углублённого поиска.",
        ],
    )
