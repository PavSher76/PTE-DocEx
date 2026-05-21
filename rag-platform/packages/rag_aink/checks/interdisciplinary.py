import re

from rag_aink.context import ProjectCheckContext
from rag_aink.registry import register
from rag_aink.schemas import CheckResult, CheckStatus

CROSS_REF = re.compile(
    r"раздел\w*\s+(АР|КЖ|ОВ|ВК|ЭО|ТХ|СС|ПОС)|"
    r"согласован\w*\s+с\s+раздел\w*\s+(АР|КЖ|ОВ|ВК|ЭО|ТХ)",
    re.IGNORECASE,
)


@register("interdisciplinary_refs", "Междисциплинарные ссылки")
def check_interdisciplinary_refs(ctx: ProjectCheckContext) -> CheckResult:
    refs: list[dict] = []
    for token in ctx.tokens:
        for match in CROSS_REF.finditer(token.text):
            refs.append(
                {
                    "target": match.group(1).upper(),
                    "source_discipline": token.discipline,
                    "page": token.page_number,
                    "text": token.text[:160],
                }
            )

    disciplines = ctx.disciplines
    missing_targets = {r["target"] for r in refs} - {d.upper() for d in disciplines if d}

    status = CheckStatus.PASSED
    if refs and missing_targets:
        status = CheckStatus.WARNING

    return CheckResult(
        check_id="interdisciplinary_refs",
        title="Междисциплинарные ссылки",
        status=status,
        summary=f"Междисциплинарных отсылок: {len(refs)}, отсутствующих разделов: {len(missing_targets)}.",
        details=[
            f"Ссылки на отсутствующие дисциплины: {', '.join(sorted(missing_targets))}"
            if missing_targets
            else "Все упомянутые разделы присутствуют в комплекте."
        ],
        evidence=refs[:20],
        recommendations=[
            "Добавьте недостающие разделы или скорректируйте перекрёстные ссылки.",
        ]
        if missing_targets
        else [],
    )
