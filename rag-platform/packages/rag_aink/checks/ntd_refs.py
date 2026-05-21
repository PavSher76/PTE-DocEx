from rag_aink.context import ProjectCheckContext
from rag_aink.registry import register
from rag_aink.schemas import CheckResult, CheckStatus
from rag_tokenizers.metadata import NTD_PATTERN


@register("ntd_references", "Проверка ссылок на НТД")
def check_ntd_references(ctx: ProjectCheckContext) -> CheckResult:
    all_refs: set[str] = set()
    tokens_with_refs: list[dict] = []
    requirements_without_ntd = []

    for token in ctx.tokens:
        refs = list(token.ntd_refs or [])
        if not refs and token.element_type == "requirement":
            found = [m.group(0) for m in NTD_PATTERN.finditer(token.text)]
            refs = found
        if refs:
            all_refs.update(refs)
            tokens_with_refs.append(
                {"refs": refs, "page": token.page_number, "type": token.element_type, "text": token.text[:160]}
            )

    for req in ctx.requirements:
        if not (req.ntd_refs or []):
            requirements_without_ntd.append({"id": str(req.id), "text": req.text[:160]})

    malformed = [r for r in all_refs if len(r) < 6 or not any(ch.isdigit() for ch in r)]

    status = CheckStatus.PASSED
    if requirements_without_ntd:
        status = CheckStatus.WARNING
    if malformed:
        status = CheckStatus.WARNING

    return CheckResult(
        check_id="ntd_references",
        title="Проверка ссылок на НТД",
        status=status,
        summary=f"Уникальных ссылок на НТД: {len(all_refs)}, требований без НТД: {len(requirements_without_ntd)}.",
        details=[
            f"Примеры НТД: {', '.join(sorted(all_refs)[:8])}" if all_refs else "Ссылки на НТД не извлечены.",
            f"Подозрительные ссылки: {', '.join(malformed[:5])}" if malformed else "—",
        ],
        evidence=tokens_with_refs[:20],
        recommendations=[
            "Для требований без НТД добавьте ссылки на СП/ГОСТ в текст или реестр.",
            "Проверьте корректность номеров нормативных документов.",
        ],
    )
