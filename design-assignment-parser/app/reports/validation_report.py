from __future__ import annotations

from pathlib import Path

from app.validators.xsd_validator import ValidationResult


def write_validation_report_md(result: ValidationResult, path: Path, *, schema_key: str) -> Path:
    lines = [
        "# Отчёт валидации XML",
        "",
        f"- **Схема:** `{schema_key}`",
        f"- **Результат:** {'✅ valid' if result.valid else '❌ invalid'}",
        "",
    ]
    if result.errors:
        lines.append("## Ошибки XSD")
        for err in result.errors[:50]:
            lines.append(f"- {err}")
        lines.append("")
    if result.missing_required_fields:
        lines.append("## Недостающие / структурные поля")
        for err in result.missing_required_fields[:30]:
            lines.append(f"- {err}")
    if result.invalid_enum_values:
        lines.append("## Некорректные enum")
        for err in result.invalid_enum_values:
            lines.append(f"- {err}")
    if result.invalid_date_values:
        lines.append("## Некорректные даты")
        for err in result.invalid_date_values:
            lines.append(f"- {err}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path
