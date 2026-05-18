from __future__ import annotations

import json
from typing import Any

DEFAULT_LEARNED_LESSONS_PROMPT = (
    "Ты эксперт управления проектами. Рассмотри данные сессии выученные уроки "
    "и выяви корневые причины указанных проект в проекте. "
    "Дай рекомендации по системному устранению корневых причин."
)


def build_learned_lessons_prompt(*, analysis_prompt: str, session_data: dict[str, Any]) -> str:
    payload = {
        "role": "project_management_expert",
        "instruction": (
            "Ответ должен быть строго JSON-объектом без Markdown и пояснений до или после JSON. "
            "Опирайся только на переданные данные сессии. "
            "Группируй однотипные проблемы в корневые причины. "
            "Рекомендации должны быть системными, а не точечными исправлениями одного эпизода."
        ),
        "task": (analysis_prompt or DEFAULT_LEARNED_LESSONS_PROMPT).strip(),
        "session_data": session_data,
        "output_contract": {
            "summary": "краткий вывод по сессии (2–4 предложения)",
            "root_causes": [
                {
                    "title": "формулировка корневой причины",
                    "description": "обоснование на основе уроков",
                    "related_lessons": ["1.1", "1.2"],
                }
            ],
            "systemic_recommendations": [
                "рекомендация по системному устранению корневой причины",
            ],
        },
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)
