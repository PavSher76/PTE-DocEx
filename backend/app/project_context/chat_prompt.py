"""Промпт и схема ответа Ollama для чата обогащения контекста проекта."""

from __future__ import annotations

import json
from typing import Any

from app.project_context.ai_bundle import InvestmentProjectPackage, build_investment_project_ai_context

DEFAULT_PROJECT_CONTEXT_CHAT_PROMPT = """Ты помощник по datacentric-контексту инвестиционно-строительного проекта.
На входе — текущий JSON-пакет InvestmentProjectPackage (narratives + assignment), опционально текст загруженного документа и диалог с пользователем.

Задачи:
1. Ответь пользователю по-русски, опираясь на пакет и документ; задавай уточняющие вопросы при нехватке данных.
2. Предложи обновлённый полный пакет suggested_package: сохрани структуру и коды справочников, дополни narratives и assignment фактами из документа и чата.
3. В changes_summary кратко перечисли, что изменилось в пакете.

Не выдумывай ОГРН/ИНН/КПП и номера НПА — используй только данные из пакета, документа или явных указаний пользователя.
Верни только JSON по схеме."""

PROJECT_CONTEXT_CHAT_RESPONSE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": ["reply", "changes_summary", "suggested_package"],
    "properties": {
        "reply": {"type": "string"},
        "changes_summary": {"type": "string"},
        "suggested_package": {"type": "object"},
    },
}

_MAX_DOCUMENT_CHARS = 14_000
_MAX_HISTORY_TURNS = 8


def build_project_context_chat_prompt(
    *,
    package: InvestmentProjectPackage,
    user_message: str,
    document_text: str | None,
    history: list[dict[str, str]],
    instruction: str,
) -> str:
    ai_context = build_investment_project_ai_context(package)
    doc_block = ""
    if document_text and document_text.strip():
        clipped = document_text.strip()
        if len(clipped) > _MAX_DOCUMENT_CHARS:
            clipped = clipped[:_MAX_DOCUMENT_CHARS] + "\n… [текст обрезан]"
        doc_block = f"\n\nТекст загруженного документа:\n---\n{clipped}\n---"

    history_lines: list[str] = []
    for turn in history[-_MAX_HISTORY_TURNS:]:
        role = turn.get("role", "user")
        content = (turn.get("content") or "").strip()
        if content:
            history_lines.append(f"{role}: {content}")
    history_block = "\n".join(history_lines) if history_lines else "(пусто)"

    return (
        f"{instruction.strip() or DEFAULT_PROJECT_CONTEXT_CHAT_PROMPT}\n\n"
        f"Текущий контекст для LLM:\n{ai_context}\n\n"
        f"Текущий пакет (JSON):\n{json.dumps(package.model_dump(mode='json'), ensure_ascii=False, indent=2)}"
        f"{doc_block}\n\n"
        f"История диалога:\n{history_block}\n\n"
        f"Сообщение пользователя:\n{user_message.strip()}"
    )
