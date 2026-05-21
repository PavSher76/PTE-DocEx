import re

from rag_aink.context import ProjectCheckContext
from rag_aink.registry import register
from rag_aink.schemas import CheckResult, CheckStatus

SOURCE_DATA_PATTERN = re.compile(
    r"исходн\w*\s+данн|исходно[- ]разреш|геолог|геодез|топосъём|топосъем|технологическ\w*\s+регламент",
    re.IGNORECASE,
)
ID_DOC_PATTERN = re.compile(r"\bИД[-–\s]?\w+", re.IGNORECASE)


@register("missing_source_data", "Проверка полноты исходных данных")
def check_missing_source_data(ctx: ProjectCheckContext) -> CheckResult:
    mentions: list[dict] = []
    for token in ctx.tokens:
        if SOURCE_DATA_PATTERN.search(token.text):
            mentions.append(
                {
                    "document_id": str(token.document_id),
                    "page": token.page_number,
                    "fragment": token.text[:200],
                }
            )

    id_docs = [d for d in ctx.documents if d.document_code and ID_DOC_PATTERN.search(d.document_code)]
    id_docs_by_name = [d for d in ctx.documents if "исходн" in d.name.lower() or d.name.lower().startswith("ид")]

    status = CheckStatus.PASSED
    recommendations: list[str] = []

    if mentions and not id_docs and not id_docs_by_name:
        status = CheckStatus.WARNING
        recommendations.append(
            "В тексте есть ссылки на исходные данные, но отдельные файлы ИД не загружены."
        )
    elif not mentions:
        status = CheckStatus.WARNING
        recommendations.append(
            "Не найдены упоминания исходных данных — проверьте раздел «Исходно-разрешительная документация»."
        )

    return CheckResult(
        check_id="missing_source_data",
        title="Проверка полноты исходных данных",
        status=status,
        summary=f"Упоминаний ИД в токенах: {len(mentions)}, загружено ИД-файлов: {len(id_docs) + len(id_docs_by_name)}.",
        details=[
            "Проверка эвристическая: поиск фраз «исходные данные», геология, топосъёмка.",
        ],
        evidence=mentions[:15],
        recommendations=recommendations,
    )
