from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class DocumentElementDTO:
    page_number: int
    element_type: str
    text: str
    bbox: list[float] | None = None
    reading_order: int = 0
    table_markdown: str | None = None
    table_csv: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class ParserAdapter(ABC):
    name: str = "base"

    @abstractmethod
    def parse(self, path: Path, file_type: str) -> list[DocumentElementDTO]:
        raise NotImplementedError
