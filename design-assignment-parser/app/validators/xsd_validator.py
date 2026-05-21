from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from lxml import etree


@dataclass
class ValidationResult:
    valid: bool
    errors: list[str] = field(default_factory=list)
    missing_required_fields: list[str] = field(default_factory=list)
    invalid_enum_values: list[str] = field(default_factory=list)
    invalid_date_values: list[str] = field(default_factory=list)


def validate_xml_against_xsd(xml_path: Path, xsd_path: Path) -> ValidationResult:
    result = ValidationResult(valid=True)
    try:
        schema_doc = etree.parse(str(xsd_path))
        schema = etree.XMLSchema(schema_doc)
        xml_doc = etree.parse(str(xml_path))
        if not schema.validate(xml_doc):
            result.valid = False
            for err in schema.error_log:
                msg = f"line {err.line}: {err.message}"
                result.errors.append(msg)
                _classify_error(msg, result)
    except etree.XMLSchemaParseError as exc:
        result.valid = False
        result.errors.append(f"XSD parse error: {exc}")
    except Exception as exc:
        result.valid = False
        result.errors.append(str(exc))
    return result


def _classify_error(msg: str, result: ValidationResult) -> None:
    lower = msg.lower()
    if "enumeration" in lower or "enum" in lower:
        result.invalid_enum_values.append(msg)
    if "date" in lower:
        result.invalid_date_values.append(msg)
    if "required" in lower or "missing" in lower or "not expected" in lower:
        result.missing_required_fields.append(msg)
