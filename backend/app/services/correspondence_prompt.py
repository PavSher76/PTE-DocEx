from typing import Any

from app.schemas import LanguageIssue

DEFAULT_CORRESPONDENCE_PROMPT = """Проверь исходящее деловое письмо.
Оцени:
- ложные срабатывания LanguageTool;
- грамматику и синтаксис;
- деловой стиль и ясность;
- этичность формулировок;
- корректность примененных терминов;
- риски некорректной трактовки адресатом.
- не считай двойные и тройные пробелы ошибками; замечания LanguageTool только про лишние интервалы, повторные пробелы или пробелы после OCR помечай accepted=false.
Верни только JSON-объект без Markdown, комментариев и пояснений."""


def build_languagetool_report(text: str, issues: list[LanguageIssue]) -> dict[str, Any]:
    issue_items = [_issue_to_prompt_json(index, issue, text) for index, issue in enumerate(issues)]
    return {
        "source": "LanguageTool",
        "language": "ru-RU",
        "summary": {
            "total": len(issue_items),
            "critical": sum(1 for issue in issue_items if issue["severity"] == "critical"),
            "warning": sum(1 for issue in issue_items if issue["severity"] == "warning"),
            "info": sum(1 for issue in issue_items if issue["severity"] == "info"),
            "categories": sorted({issue["category"] for issue in issue_items if issue["category"]}),
        },
        "issues": issue_items,
    }


def build_correspondence_prompt(
    *,
    check_prompt: str,
    letter_text: str,
    terminology: list[str],
    business_context: str,
    strictness: str,
    languagetool_report: dict[str, Any],
) -> str:
    payload = {
        "role": "local_quality_control_assistant",
        "instruction": (
            "Ответ должен быть строго JSON-объектом с двумя верхнеуровневыми ключами: "
            "issues и style_assessment. Не добавляй Markdown, текст до JSON или текст после JSON. "
            "Не включай двойные и тройные пробелы в список ошибок; если замечание LanguageTool "
            "связано только с лишними пробелами, верни для него accepted=false."
        ),
        "task": check_prompt.strip() or DEFAULT_CORRESPONDENCE_PROMPT,
        "strictness": strictness,
        "business_context": business_context.strip(),
        "terminology": terminology,
        "letter_text": letter_text,
        "languagetool_result": languagetool_report,
        "output_contract": {
            "required_top_level_keys": ["issues", "style_assessment"],
            "issues": [
                {
                    "issue_index": 0,
                    "accepted": True,
                    "severity": "info | warning | critical",
                    "reason": "почему замечание нужно показать или скрыть",
                }
            ],
            "style_assessment": {
                "status": "OK | Требует проверки | Критично",
                "tone": "оценка делового тона",
                "ethics": "оценка этичности",
                "terminology": "оценка корректности терминов",
                "recommendations": ["конкретные рекомендации"],
            },
        },
    }
    return _to_json(payload)


def _issue_to_prompt_json(index: int, issue: LanguageIssue, text: str) -> dict[str, Any]:
    fragment = ""
    if issue.offset is not None and issue.length is not None:
        fragment = text[issue.offset : issue.offset + issue.length]

    return {
        "issue_index": index,
        "rule_id": issue.rule_id,
        "category": issue.category,
        "message": issue.message,
        "short_message": issue.short_message,
        "severity": issue.severity,
        "offset": issue.offset,
        "length": issue.length,
        "fragment": fragment,
        "context": issue.context,
        "replacements": issue.replacements,
    }


def _to_json(payload: dict[str, Any]) -> str:
    import json

    return json.dumps(payload, ensure_ascii=False, indent=2)
