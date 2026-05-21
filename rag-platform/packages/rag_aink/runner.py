from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy.orm import Session

from rag_aink import checks  # noqa: F401 — регистрация проверок
from rag_aink.context import load_project_context
from rag_aink.registry import REGISTRY, list_checks
from rag_aink.report import render_markdown
from rag_aink.schemas import CheckReport, CheckResult, CheckStatus


class CheckRunner:
    def __init__(self, session: Session):
        self._session = session

    def available_checks(self) -> list[dict[str, str]]:
        return list_checks()

    def run(
        self,
        project_id: str,
        *,
        check_ids: list[str] | None = None,
        run_id: UUID | None = None,
    ) -> tuple[CheckReport, str]:
        ctx = load_project_context(self._session, project_id)
        selected = check_ids or list(REGISTRY.keys())
        results = []
        for cid in selected:
            entry = REGISTRY.get(cid)
            if entry is None:
                results.append(
                    CheckResult(
                        check_id=cid,
                        title=cid,
                        status=CheckStatus.SKIPPED,
                        summary="Неизвестная проверка.",
                    )
                )
                continue
            _title, fn = entry
            results.append(fn(ctx))

        report = CheckReport(
            run_id=run_id or uuid4(),
            project_id=project_id,
            created_at=datetime.now(timezone.utc),
            overall_status=CheckStatus.PASSED,
            checks=results,
            summary=self._build_summary(results),
        )
        report.compute_stats()
        markdown = render_markdown(report)
        return report, markdown

    def _build_summary(self, results: list) -> str:
        failed = sum(1 for r in results if r.status == CheckStatus.FAILED)
        warnings = sum(1 for r in results if r.status == CheckStatus.WARNING)
        if failed:
            return f"Выполнено проверок: {len(results)}. Критичных замечаний: {failed}."
        if warnings:
            return f"Выполнено проверок: {len(results)}. Предупреждений: {warnings}."
        return f"Выполнено проверок: {len(results)}. Критичных замечаний не выявлено."
