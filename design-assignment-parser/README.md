# Design Assignment Parser

Сервис разбора PDF **«Задание на проектирование»** в валидируемый XML по XSD Минстроя РФ.

**Принцип:** `PDF → canonical JSON → validated XML → RAG tokens` (не OCR → XML напрямую).

## Версия схемы

| Ключ | XSD | В силе с | Опубликована |
|------|-----|----------|--------------|
| `v01_00` | `DesignAssignment-01-00` | 2025-07-09 | 2025-04-09 |

Конфиг: `ACTIVE_MINSTROY_DESIGN_ASSIGNMENT_SCHEMA_VERSION=v01_00`

Файлы: `schemas/minstroy/design_assignment/v01_00/schema.xsd`, `mapping.yaml`, `meta.yaml`.

## Пайплайн (14 этапов)

1. ingest PDF  
2. detect PDF type (born-digital / raster / mixed)  
3. extract text layer (PyMuPDF)  
4–5. render + OCR при необходимости (Tesseract, 300 DPI)  
6. layout detection  
7. section extraction  
8. field extraction → **canonical JSON**  
9. normalize + `corrections.yaml`  
10. map via `mapping.yaml`  
11. export JSON  
12. generate XML  
13. validate XSD (lxml)  
14. quality + validation reports  

## API

| Метод | Путь |
|-------|------|
| POST | `/parse-design-assignment` |
| GET | `/jobs/{job_id}` |
| GET | `/jobs/{job_id}/canonical-json` |
| GET | `/jobs/{job_id}/xml` |
| GET | `/jobs/{job_id}/validation-report` |
| GET | `/jobs/{job_id}/tokens` |

## Запуск

```bash
cd design-assignment-parser
pip install -e ".[dev]"
uvicorn app.main:app --reload --port 8200
```

Docker:

```bash
docker compose up --build
```

## Артефакты job

- `canonical.json`
- `design_assignment.xml`
- `requirements.json`
- `rag_tokens.json`
- `traceability.json`
- `validation_report.md`
- `quality_report.json`

## Human-in-the-loop

См. `corrections.example.yaml` — переопределение полей canonical перед XML.

## Тесты

```bash
pytest -q
```

## Связь с PTE-DocEx

- XSD совпадает с `backend/app/data/minstroy/DesignAssignment-01-00.xsd`
- Логика извлечения текста — как `backend/app/services/pdf_text.py` (переписка)
- Экспорт XML в проекте контекста: `backend/app/project_context/xml_design_assignment.py`
