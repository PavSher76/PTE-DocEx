from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from rag_aink.runner import CheckRunner
from rag_aink.schemas import CheckStatus
from rag_llm.service import QueryAnswerService
from rag_retrievers.hybrid import HybridRetriever
from rag_schemas.pilot import PilotRunResponse, PilotSourceDataIssue
from rag_schemas.query import SearchFilters
from rag_storage.config import Settings, get_settings
from rag_storage.models import Document, Requirement
from rag_storage.repositories.project import ProjectRepository

ITC_PROJECT_NAME = "Пилот ИТЦ — комплект ПД/РД"
ITC_PROJECT_DESCRIPTION = (
    "Пилотный проект для проверки RAG-конвейера: состав комплекта, "
    "исходные данные, реестр требований, AI-NK."
)

SOURCE_DATA_CHECK_IDS = frozenset({"missing_source_data", "document_set_completeness"})


class PilotRunner:
    def __init__(self, session: Session, settings: Settings | None = None):
        self._session = session
        self._settings = settings or get_settings()

    def bootstrap(self, project_id: str | None = None) -> tuple[str, bool]:
        pid = project_id or self._settings.pilot_default_project_id
        repo = ProjectRepository(self._session)
        existing = repo.get_by_project_id(pid)
        if existing:
            return pid, False
        repo.create(pid, ITC_PROJECT_NAME, ITC_PROJECT_DESCRIPTION)
        self._session.commit()
        return pid, True

    def run(
        self,
        project_id: str,
        *,
        check_ids: list[str] | None = None,
        run_query: str | None = None,
    ) -> PilotRunResponse:
        if ProjectRepository(self._session).get_by_project_id(project_id) is None:
            raise ValueError(f"Проект {project_id} не найден. Вызовите POST /pilot/bootstrap.")

        check_runner = CheckRunner(self._session)
        report, markdown = check_runner.run(project_id, check_ids=check_ids)

        from rag_storage.models import CheckRun

        row = CheckRun(
            id=report.run_id,
            project_id=project_id,
            overall_status=report.overall_status.value,
            report_json=report.model_dump(mode="json"),
            report_markdown=markdown,
        )
        self._session.add(row)
        self._session.commit()

        project = ProjectRepository(self._session).get_by_project_id(project_id)
        docs_count = (
            self._session.scalar(
                select(func.count(Document.id)).where(Document.project_uuid == project.id)
            )
            if project
            else 0
        )

        req_count = self._session.scalar(
            select(func.count(Requirement.id)).where(Requirement.project_id == project_id)
        ) or 0

        source_issues = self._extract_source_data_issues(report)

        query_answer: str | None = None
        if run_query:
            hits = HybridRetriever(self._settings).search(
                project_id=project_id,
                query=run_query,
                filters=SearchFilters(),
                top_k=8,
                use_hybrid=True,
                rerank=True,
            )
            query_answer, _ = QueryAnswerService(self._settings).answer(
                run_query, hits[:8], use_llm=self._settings.llm_enabled
            )

        return PilotRunResponse(
            project_id=project_id,
            documents_count=int(docs_count or 0),
            requirements_count=int(req_count),
            check_report=report,
            source_data_issues=source_issues,
            query_answer=query_answer,
            markdown_url_hint=f"/projects/{project_id}/checks/{report.run_id}/report.md",
            run_id=report.run_id,
        )

    def _extract_source_data_issues(self, report) -> list[PilotSourceDataIssue]:
        issues: list[PilotSourceDataIssue] = []
        for check in report.checks:
            if check.check_id not in SOURCE_DATA_CHECK_IDS:
                continue
            if check.status in {CheckStatus.PASSED, CheckStatus.SKIPPED}:
                continue
            issues.append(
                PilotSourceDataIssue(
                    check_id=check.check_id,
                    summary=check.summary,
                    details=list(check.details or [])[:10],
                )
            )
        return issues
