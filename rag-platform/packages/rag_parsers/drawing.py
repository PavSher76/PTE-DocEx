"""Интерфейсы DWG/IFC (этап 10 — вне MVP)."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class DrawingObjectToken:
    object_id: str
    ifc_guid: str | None = None
    class_name: str = ""
    system: str = ""
    location: str = ""
    parameters: dict[str, Any] = field(default_factory=dict)
    source_model: str = ""


class DrawingParser(ABC):
    @abstractmethod
    def extract(self, path: str) -> list[DrawingObjectToken]:
        raise NotImplementedError


class IfcParser(ABC):
    @abstractmethod
    def extract_objects(self, path: str) -> list[DrawingObjectToken]:
        raise NotImplementedError


class DwgToPdfAdapter:
    """Заглушка: DWG → PDF/SVG."""

    def convert(self, _path: str) -> str:
        raise NotImplementedError("DwgToPdfAdapter — этап 10")


class DxfTextExtractor:
    def extract(self, _path: str) -> list[str]:
        raise NotImplementedError("DxfTextExtractor — этап 10")


class IfcObjectExtractor(IfcParser):
    def extract_objects(self, _path: str) -> list[DrawingObjectToken]:
        raise NotImplementedError("IfcObjectExtractor — этап 10")
