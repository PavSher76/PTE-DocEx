import json
import re
from typing import Any

import httpx
from pydantic import ValidationError

from app.config import Settings
from app.schemas import LanguageIssue, StyleAssessment

CORRESPONDENCE_RESPONSE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": ["issues", "style_assessment"],
    "properties": {
        "issues": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["issue_index", "accepted", "severity", "reason"],
                "properties": {
                    "issue_index": {"type": "integer"},
                    "accepted": {"type": "boolean"},
                    "severity": {"type": "string", "enum": ["info", "warning", "critical"]},
                    "reason": {"type": "string"},
                },
            },
        },
        "style_assessment": {
            "type": "object",
            "additionalProperties": False,
            "required": ["status", "tone", "ethics", "terminology", "recommendations"],
            "properties": {
                "status": {"type": "string", "enum": ["OK", "Требует проверки", "Критично"]},
                "tone": {"type": "string"},
                "ethics": {"type": "string"},
                "terminology": {"type": "string"},
                "recommendations": {"type": "array", "items": {"type": "string"}},
            },
        },
    },
}

STYLE_RESPONSE_SCHEMA = CORRESPONDENCE_RESPONSE_SCHEMA["properties"]["style_assessment"]
ISSUES_RESPONSE_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["issues"],
    "properties": {"issues": CORRESPONDENCE_RESPONSE_SCHEMA["properties"]["issues"]},
}


class OllamaClient:
    def __init__(self, settings: Settings):
        self.settings = settings

    async def analyze_correspondence(
        self,
        *,
        prompt: str,
        issues: list[LanguageIssue],
    ) -> tuple[list[LanguageIssue], StyleAssessment]:
        data = await self._generate_json(prompt, schema=CORRESPONDENCE_RESPONSE_SCHEMA)
        if not isinstance(data, dict):
            return issues, self._fallback_style("Ollama недоступен или вернул неструктурированный ответ.")

        filtered_issues = self._apply_issue_filter(issues, _find_key(data, "issues"))
        style_assessment = self._parse_style(_find_style_assessment(data))
        return filtered_issues, style_assessment

    async def filter_language_issues(self, text: str, issues: list[LanguageIssue]) -> list[LanguageIssue]:
        if not issues:
            return []

        payload = {
            "task": "Отфильтруй ложные срабатывания LanguageTool для деловой исходящей переписки.",
            "rules": [
                "Верни только JSON-объект с полем issues.",
                "Для каждого замечания сохрани индекс issue_index.",
                "accepted=true означает, что замечание нужно показать пользователю.",
                "severity: info, warning или critical.",
                "reason: краткое объяснение на русском языке.",
            ],
            "response_schema": {
                "issues": [
                    {
                        "issue_index": 0,
                        "accepted": True,
                        "severity": "info | warning | critical",
                        "reason": "краткое объяснение",
                    }
                ]
            },
            "text": text,
            "issues": [issue.model_dump() for issue in issues],
        }
        prompt = json.dumps(payload, ensure_ascii=False)
        data = await self._generate_json(prompt, schema=ISSUES_RESPONSE_SCHEMA)
        if isinstance(data, dict):
            data = _find_key(data, "issues")
        return self._apply_issue_filter(issues, data)

    def _apply_issue_filter(self, issues: list[LanguageIssue], data: Any) -> list[LanguageIssue]:
        if not issues:
            return []
        if not isinstance(data, list):
            return issues
        by_index = {item.get("issue_index"): item for item in data if isinstance(item, dict)}
        filtered: list[LanguageIssue] = []
        for index, issue in enumerate(issues):
            update = by_index.get(index)
            if not update:
                filtered.append(issue)
                continue

            accepted = _as_bool(update.get("accepted", issue.accepted))
            severity = update.get("severity", issue.severity)
            if severity not in {"info", "warning", "critical"}:
                severity = issue.severity

            updated = issue.model_copy(
                update={
                    "accepted": accepted,
                    "severity": severity,
                    "reason": str(update.get("reason") or issue.reason or ""),
                }
            )
            if updated.accepted:
                filtered.append(updated)

        return filtered

    async def assess_style(self, text: str, terminology: list[str]) -> StyleAssessment:
        payload = {
            "task": "Оцени исходящую деловую переписку.",
            "criteria": [
                "стилистика и ясность",
                "этичность и отсутствие некорректных формулировок",
                "корректность терминов из словаря",
                "деловой тон",
            ],
            "terminology": terminology,
            "response_schema": {
                "status": "OK | Требует проверки | Критично",
                "tone": "краткая оценка",
                "ethics": "краткая оценка",
                "terminology": "краткая оценка",
                "recommendations": ["список конкретных рекомендаций"],
            },
            "text": text,
        }
        data = await self._generate_json(json.dumps(payload, ensure_ascii=False), schema=STYLE_RESPONSE_SCHEMA)
        return self._parse_style(data)

    def _parse_style(self, data: Any) -> StyleAssessment:
        if not isinstance(data, dict):
            return self._fallback_style("Ollama недоступен или вернул неструктурированный ответ.")
        try:
            return StyleAssessment.model_validate(data)
        except ValidationError:
            return self._fallback_style("Не удалось разобрать оценку Ollama.")

    async def _generate_json(self, prompt: str, schema: dict[str, Any] | None = None) -> Any:
        url = f"{self.settings.ollama_base_url.rstrip('/')}/api/generate"
        request_payload = {
            "model": self.settings.ollama_model,
            "prompt": prompt,
            "stream": False,
            "format": schema or "json",
            "options": {"temperature": 0.0},
        }
        try:
            async with httpx.AsyncClient(timeout=self.settings.ollama_timeout_seconds) as client:
                response = await client.post(url, json=request_payload)
                response.raise_for_status()
        except httpx.HTTPError:
            return None

        return _parse_json_response(response.json().get("response", ""))

    def _fallback_style(self, reason: str) -> StyleAssessment:
        return StyleAssessment(
            status="Требует проверки",
            tone="Автоматическая оценка не выполнена",
            ethics="Автоматическая оценка не выполнена",
            terminology="Автоматическая оценка не выполнена",
            recommendations=[reason, "Проверьте текст вручную или запустите локальную модель Ollama."],
        )


def _as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"true", "1", "yes", "да"}
    return bool(value)


def _parse_json_response(raw_response: Any) -> Any:
    if isinstance(raw_response, (dict, list)):
        return raw_response
    if not isinstance(raw_response, str):
        return None

    response = raw_response.strip()
    for candidate in (response, _strip_code_fence(response), _extract_json_object(response)):
        if not candidate:
            continue
        try:
            parsed = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        return _unwrap_json_string(parsed)
    return None


def _strip_code_fence(value: str) -> str:
    match = re.search(r"```(?:json)?\s*(.*?)\s*```", value, flags=re.DOTALL | re.IGNORECASE)
    return match.group(1).strip() if match else value


def _extract_json_object(value: str) -> str:
    start = value.find("{")
    end = value.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return ""
    return value[start : end + 1]


def _unwrap_json_string(value: Any) -> Any:
    if isinstance(value, str):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value
    return value


def _find_style_assessment(data: dict[str, Any]) -> Any:
    style = _find_key(data, "style_assessment")
    if style is not None:
        return style
    if {"status", "tone", "ethics", "terminology"}.issubset(data.keys()):
        return data
    return None


def _find_key(data: Any, key: str) -> Any:
    if isinstance(data, dict):
        if key in data:
            return data[key]
        for value in data.values():
            found = _find_key(value, key)
            if found is not None:
                return found
    if isinstance(data, list):
        for item in data:
            found = _find_key(item, key)
            if found is not None:
                return found
    return None
