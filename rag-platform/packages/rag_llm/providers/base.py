from abc import ABC, abstractmethod


class LLMProvider(ABC):
    @abstractmethod
    def generate(self, prompt: str, *, model: str | None = None) -> str | None:
        """Сгенерировать текст; None при недоступности провайдера."""

    @abstractmethod
    def list_models(self) -> list[str]:
        pass
