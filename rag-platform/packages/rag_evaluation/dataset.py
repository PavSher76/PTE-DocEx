"""Golden dataset для регрессии retrieval (этап 13)."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

DEFAULT_GOLDEN_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "evaluation" / "golden_questions.json"


@dataclass
class GoldenQuestion:
    id: str
    project_id: str
    query: str
    expected_token_ids: list[str]
    min_precision_at_5: float = 0.0
    notes: str = ""


def load_golden_dataset(path: Path | None = None) -> list[GoldenQuestion]:
    p = path or DEFAULT_GOLDEN_PATH
    if not p.exists():
        return []
    raw = json.loads(p.read_text(encoding="utf-8"))
    items = raw if isinstance(raw, list) else raw.get("questions", [])
    return [
        GoldenQuestion(
            id=str(item["id"]),
            project_id=str(item["project_id"]),
            query=str(item["query"]),
            expected_token_ids=[str(x) for x in item.get("expected_token_ids", [])],
            min_precision_at_5=float(item.get("min_precision_at_5", 0.0)),
            notes=str(item.get("notes", "")),
        )
        for item in items
    ]
