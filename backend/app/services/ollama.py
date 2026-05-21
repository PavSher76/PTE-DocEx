import json
import logging
import re
from dataclasses import dataclass
from typing import Any

import httpx
from pydantic import ValidationError

from app.config import Settings
from app.project_context.chat_prompt import PROJECT_CONTEXT_CHAT_RESPONSE_SCHEMA
from app.schemas import LanguageIssue, LearnedLessonsAnalysis, StyleAssessment

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

LEARNED_LESSONS_RESPONSE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": ["summary", "root_causes", "systemic_recommendations"],
    "properties": {
        "summary": {"type": "string"},
        "root_causes": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["title", "description", "related_lessons"],
                "properties": {
                    "title": {"type": "string"},
                    "description": {"type": "string"},
                    "related_lessons": {"type": "array", "items": {"type": "string"}},
                },
            },
        },
        "systemic_recommendations": {"type": "array", "items": {"type": "string"}},
    },
}


logger = logging.getLogger(__name__)


def _ollama_candidate_urls(base_url: str) -> list[str]:
    """Пробуем основной URL и типичные запасные (Docker ↔ хост)."""
    base = base_url.rstrip("/")
    candidates = [base]
    fallbacks = {
        "http://host.docker.internal:11434": "http://127.0.0.1:11434",
        "http://127.0.0.1:11434": "http://host.docker.internal:11434",
        "http://localhost:11434": "http://127.0.0.1:11434",
    }
    alt = fallbacks.get(base)
    if alt and alt not in candidates:
        candidates.append(alt)
    return candidates


@dataclass
class OllamaModelsResult:
    models: list[str]
    error: str | None = None


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

    async def chat_project_context(self, *, prompt: str, model: str | None = None) -> dict[str, Any] | None:
        data = await self._generate_json(prompt, schema=PROJECT_CONTEXT_CHAT_RESPONSE_SCHEMA, model=model)
        return data if isinstance(data, dict) else None

    async def analyze_learned_lessons(self, *, prompt: str, model: str | None = None) -> LearnedLessonsAnalysis:
        data = await self._generate_json(prompt, schema=LEARNED_LESSONS_RESPONSE_SCHEMA, model=model)
        if not isinstance(data, dict):
            return self._fallback_learned_lessons("Ollama недоступен или вернул неструктурированный ответ.")
        try:
            return LearnedLessonsAnalysis.model_validate(data)
        except ValidationError:
            return self._fallback_learned_lessons("Не удалось разобрать ответ Ollama.")

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

    async def list_models(self) -> OllamaModelsResult:
        errors: list[str] = []
        for base in _ollama_candidate_urls(self.settings.ollama_base_url):
            url = f"{base}/api/tags"
            try:
                async with httpx.AsyncClient(timeout=10.0, trust_env=False) as client:
                    response = await client.get(url)
                    response.raise_for_status()
            except httpx.HTTPError as exc:
                logger.warning("Ollama /api/tags failed at %s: %s", url, exc)
                errors.append(f"{base}: {exc}")
                continue

            try:
                payload = response.json()
            except ValueError as exc:
                logger.warning("Ollama /api/tags invalid JSON at %s: %s", url, exc)
                errors.append(f"{base}: некорректный JSON")
                continue

            raw_models = payload.get("models") if isinstance(payload, dict) else None
            if not isinstance(raw_models, list):
                raw_models = []

            names: list[str] = []
            for item in raw_models:
                if isinstance(item, dict) and item.get("name"):
                    names.append(str(item["name"]))
            if names:
                return OllamaModelsResult(models=sorted(names))
            errors.append(f"{base}: список моделей пуст")

        detail = errors[0] if len(errors) == 1 else "; ".join(errors)
        return OllamaModelsResult(
            models=[],
            error=(
                f"Ollama недоступна ({self.settings.ollama_base_url}). "
                f"Запустите на хосте: ollama serve. Детали: {detail}"
            ),
        )

    async def _generate_json(
        self,
        prompt: str,
        schema: dict[str, Any] | None = None,
        *,
        model: str | None = None,
    ) -> Any:
        url = f"{self.settings.ollama_base_url.rstrip('/')}/api/generate"
        request_payload = {
            "model": model or self.settings.ollama_model,
            "prompt": prompt,
            "stream": False,
            "format": schema or "json",
            "options": {"temperature": 0.0},
        }
        try:
            async with httpx.AsyncClient(timeout=self.settings.ollama_timeout_seconds, trust_env=False) as client:
                response = await client.post(url, json=request_payload)
                response.raise_for_status()
        except httpx.HTTPError as exc:
            logger.warning("Ollama /api/generate failed at %s: %s", url, exc)
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

    def _fallback_learned_lessons(self, reason: str) -> LearnedLessonsAnalysis:
        return LearnedLessonsAnalysis(
            summary="Автоматический анализ не выполнен.",
            root_causes=[],
            systemic_recommendations=[reason, "Проверьте данные формы или запустите локальную модель Ollama."],
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
