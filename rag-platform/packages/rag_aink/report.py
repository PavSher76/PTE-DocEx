"""Генерация отчётов AI-NK: JSON + Markdown."""

from __future__ import annotations

from rag_aink.schemas import CheckReport, CheckStatus


def render_markdown(report: CheckReport) -> str:
    lines = [
        f"# Отчёт AI-NK — проект `{report.project_id}`",
        "",
        f"- **Дата:** {report.created_at.isoformat()}",
        f"- **Итог:** {report.overall_status.value.upper()}",
        f"- **Run ID:** `{report.run_id}`",
        "",
        report.summary,
        "",
        "## Сводка",
        "",
        "| Статус | Количество |",
        "|--------|------------|",
    ]
    for status in CheckStatus:
        count = report.stats.get(status.value, 0)
        if count:
            lines.append(f"| {status.value} | {count} |")

    lines.extend(["", "## Проверки", ""])
    for check in report.checks:
        icon = {"passed": "✅", "warning": "⚠️", "failed": "❌", "skipped": "⏭️"}.get(
            check.status.value, "•"
        )
        lines.append(f"### {icon} {check.title}")
        lines.append("")
        lines.append(f"**Статус:** `{check.status.value}` — {check.summary}")
        lines.append("")
        if check.details:
            lines.append("**Детали:**")
            for detail in check.details:
                lines.append(f"- {detail}")
            lines.append("")
        if check.recommendations:
            lines.append("**Рекомендации:**")
            for rec in check.recommendations:
                lines.append(f"- {rec}")
            lines.append("")
    return "\n".join(lines)
