from __future__ import annotations

from typing import Callable

from rag_aink.context import ProjectCheckContext
from rag_aink.schemas import CheckResult

CheckFn = Callable[[ProjectCheckContext], CheckResult]

REGISTRY: dict[str, tuple[str, CheckFn]] = {}


def register(check_id: str, title: str):
    def decorator(fn: CheckFn) -> CheckFn:
        REGISTRY[check_id] = (title, fn)
        return fn

    return decorator


def list_checks() -> list[dict[str, str]]:
    return [{"id": cid, "title": meta[0]} for cid, meta in REGISTRY.items()]
