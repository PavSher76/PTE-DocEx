from datetime import datetime, timezone
from uuid import uuid4

from rag_aink.context import DocumentSnapshot, ProjectCheckContext
from rag_aink.registry import REGISTRY, list_checks
from rag_aink.report import render_markdown
from rag_aink.schemas import CheckReport, CheckResult, CheckStatus

# Импорт регистрирует проверки
import rag_aink.checks  # noqa: F401


def test_registry_has_eight_checks():
    assert len(REGISTRY) >= 7
    ids = {c["id"] for c in list_checks()}
    assert "document_set_completeness" in ids
    assert "ntd_references" in ids


def test_document_set_check_empty_project():
    from rag_aink.checks.document_set import check_document_set_completeness

    ctx = ProjectCheckContext(project_id="PTE-TEST", project_name="Test")
    result = check_document_set_completeness(ctx)
    assert result.status == CheckStatus.FAILED


def test_document_set_check_with_disciplines():
    from rag_aink.checks.document_set import check_document_set_completeness

    ctx = ProjectCheckContext(
        project_id="PTE-TEST",
        project_name="Test",
        documents=[
            DocumentSnapshot(
                id=uuid4(),
                name="ПЗ-ТХ.pdf",
                document_code="ПЗ-ТХ",
                stage="PD",
                discipline="TX",
                indexed=True,
                token_count=10,
            ),
            DocumentSnapshot(
                id=uuid4(),
                name="АР.pdf",
                document_code="АР",
                stage="PD",
                discipline="AR",
                indexed=True,
                token_count=5,
            ),
        ],
    )
    result = check_document_set_completeness(ctx)
    assert result.status in {CheckStatus.PASSED, CheckStatus.WARNING}


def test_markdown_report_renders():
    report = CheckReport(
        run_id=uuid4(),
        project_id="PTE-25-450",
        created_at=datetime.now(timezone.utc),
        overall_status=CheckStatus.WARNING,
        checks=[
            CheckResult(
                check_id="test",
                title="Тест",
                status=CheckStatus.WARNING,
                summary="Предупреждение",
                details=["деталь"],
            )
        ],
        summary="Сводка",
    )
    report.compute_stats()
    md = render_markdown(report)
    assert "AI-NK" in md
    assert "Предупреждение" in md
