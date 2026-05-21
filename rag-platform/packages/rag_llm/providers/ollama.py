from __future__ import annotations

import logging

import httpx

from rag_llm.providers.base import LLMProvider
from rag_storage.config import Settings

logger = logging.getLogger(__name__)


class OllamaProvider(LLMProvider):
    def __init__(self, settings: Settings):
        self._settings = settings
        self._base = settings.ollama_base_url.rstrip("/")

    def generate(self, prompt: str, *, model: str | None = None) -> str | None:
        url = f"{self._base}/api/generate"
        payload = {
            "model": model or self._settings.ollama_model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.1},
        }
        try:
            with httpx.Client(timeout=self._settings.ollama_timeout_seconds, trust_env=False) as client:
                response = client.post(url, json=payload)
                response.raise_for_status()
        except httpx.HTTPError as exc:
            logger.warning("Ollama generate failed: %s", exc)
            return None
        data = response.json()
        text = data.get("response", "")
        return str(text).strip() if text else None

    def list_models(self) -> list[str]:
        url = f"{self._base}/api/tags"
        try:
            with httpx.Client(timeout=10.0, trust_env=False) as client:
                response = client.get(url)
                response.raise_for_status()
        except httpx.HTTPError:
            return []
        models = response.json().get("models", [])
        return sorted(str(m["name"]) for m in models if isinstance(m, dict) and m.get("name"))
