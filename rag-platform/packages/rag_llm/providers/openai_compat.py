from __future__ import annotations

import logging

import httpx

from rag_llm.providers.base import LLMProvider
from rag_storage.config import Settings

logger = logging.getLogger(__name__)


class OpenAICompatProvider(LLMProvider):
    """OpenAI-совместимый API (/v1/chat/completions)."""

    def __init__(self, settings: Settings):
        self._settings = settings
        self._base = (settings.openai_api_base or "").rstrip("/")
        self._key = settings.openai_api_key or ""

    def _enabled(self) -> bool:
        return bool(self._base and self._key)

    def generate(self, prompt: str, *, model: str | None = None) -> str | None:
        if not self._enabled():
            return None
        url = f"{self._base}/v1/chat/completions"
        headers = {"Authorization": f"Bearer {self._key}"}
        payload = {
            "model": model or self._settings.ollama_model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.1,
        }
        try:
            with httpx.Client(timeout=self._settings.ollama_timeout_seconds, trust_env=False) as client:
                response = client.post(url, json=payload, headers=headers)
                response.raise_for_status()
        except httpx.HTTPError as exc:
            logger.warning("OpenAI-compat generate failed: %s", exc)
            return None
        data = response.json()
        choices = data.get("choices") or []
        if not choices:
            return None
        message = choices[0].get("message") or {}
        content = message.get("content", "")
        return str(content).strip() if content else None

    def list_models(self) -> list[str]:
        return []
