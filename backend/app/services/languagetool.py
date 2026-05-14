from typing import Any

import httpx

from app.config import Settings
from app.schemas import LanguageIssue


class LanguageToolClient:
    def __init__(self, settings: Settings):
        self.settings = settings

    async def check(self, text: str) -> list[LanguageIssue]:
        payload = {
            "text": text,
            "language": self.settings.languagetool_language,
            "enabledOnly": "false",
        }
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(self.settings.languagetool_url, data=payload)
                response.raise_for_status()
        except httpx.HTTPError as exc:
            return [
                LanguageIssue(
                    message=f"LanguageTool недоступен: {exc}",
                    category="system",
                    severity="critical",
                    accepted=True,
                    reason="Проверка синтаксиса не выполнена",
                )
            ]

        return [self._map_match(match) for match in response.json().get("matches", [])]

    def _map_match(self, match: dict[str, Any]) -> LanguageIssue:
        context = match.get("context", {})
        rule = match.get("rule", {})
        category = rule.get("category", {})
        replacements = [item.get("value", "") for item in match.get("replacements", [])[:5]]
        issue_type = rule.get("issueType") or category.get("id")
        severity = "critical" if issue_type in {"misspelling", "grammar"} else "warning"

        return LanguageIssue(
            message=match.get("message", "Замечание LanguageTool"),
            short_message=match.get("shortMessage") or None,
            offset=match.get("offset"),
            length=match.get("length"),
            context=context.get("text"),
            rule_id=rule.get("id"),
            category=category.get("name") or category.get("id"),
            replacements=[value for value in replacements if value],
            severity=severity,
            accepted=True,
        )
