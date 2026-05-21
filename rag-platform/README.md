# RAG Platform — конвейер ПД/РД

Локальный RAG для инженерной документации: **не «чат с PDF»**, а конвейер превращения ПД/РД в **инженерные токены** с hybrid search и цитированием (документ, страница, bbox).

## Архитектура MVP (Sprint 1)

```
PDF/DOCX/XLSX → MinIO → Worker (RQ) → parse → tokenize → embed → Qdrant
                              ↓
                         PostgreSQL (метаданные, токены, jobs)
                              ↓
                         FastAPI → /search, /query (citations)
```

**Инфраструктура:** PostgreSQL, Qdrant (dense + sparse collections), MinIO, Redis (RQ).

## Быстрый старт

```bash
cd rag-platform
cp .env.example .env
make install
make up          # postgres, redis, minio, qdrant
make migrate     # alembic (нужен поднятый postgres)

# В двух терминалах:
make dev-api
make dev-worker

# Проверка
make health
make ingest-sample
make query
```

Или всё в Docker:

```bash
make up-all
make health
```

## API (Sprint 1)

| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/health` | Liveness |
| GET | `/health/ready` | Postgres + Qdrant + MinIO |
| POST | `/projects` | Создать проект |
| POST | `/documents/upload` | Загрузка в MinIO + job |
| GET | `/documents/{id}/status` | Статус job |
| GET | `/documents/{id}/tokens` | Инженерные токены |
| POST | `/search` | Dense search (MVP) |
| POST | `/query` | Ответ + citations |

## Структура

```
rag-platform/
  apps/api/          FastAPI
  apps/worker/       RQ worker + pipeline
  apps/admin-ui/     React UI (этап 14, заглушка)
  packages/
    rag_schemas/     Pydantic
    rag_storage/     SQLAlchemy, MinIO, Qdrant
    rag_parsers/     Docling / Unstructured (этап 4)
    rag_tokenizers/  EngineeringTokenizer (этап 5)
    rag_embeddings/  Dense (этап 6)
    rag_retrievers/  Hybrid (этап 7)
    rag_evaluation/  Метрики (этап 13)
  infra/docker-compose.yml
  alembic/
  tests/
```

## Коллекция «Анализ проекта»

Документы из PTE-DocEx (раздел **Анализ проекта**) индексируются в Qdrant:

| Коллекция | Назначение |
|-----------|------------|
| `project_analysis_text` | Инженерные токены (парсинг + токенизация) |
| `project_analysis_drawings_text` | OCR чертежей и штампы |

Загрузка: `POST /documents/upload` с `rag_collection=project_analysis`.  
Поиск: `POST /search/project-analysis`.

## Sprint 5 — Пилот ИТЦ

### LLM-ответы (этап 8)

`POST /query` с `use_llm: true` — Ollama или OpenAI-compatible API, guard «только из контекста».

```bash
curl -X POST http://127.0.0.1:8100/query \
  -H 'Content-Type: application/json' \
  -d '{"project_id":"PTE-ITC-450","query":"Какие исходные данные для ТХ?","use_llm":true}'

curl http://127.0.0.1:8100/llm/models
```

### Пилот ИТЦ

```bash
make migrate
make pilot-itc          # bootstrap + sample + полный прогон
# или по шагам:
curl -X POST http://127.0.0.1:8100/pilot/bootstrap
curl -X POST http://127.0.0.1:8100/pilot/PTE-ITC-450/run -d '{}'
curl -X POST http://127.0.0.1:8100/pilot/feedback -H 'Content-Type: application/json' \
  -d '{"project_id":"PTE-ITC-450","source_type":"pilot_run","rating":4,"comment":"...","lesson_tags":["source_data"]}'
```

### Admin UI (этап 14)

```bash
make dev-admin   # http://127.0.0.1:5174 — upload, query, AI-NK, пилот, Lessons Learned
```

### Evaluation (этап 13)

Golden dataset: `data/evaluation/golden_questions.json`. Метрики: `packages/rag_evaluation/`.

```bash
make test   # включает test_sprint5.py
```

## Sprint 4 — AI-NK

Автоматические проверки комплекта ПД/РД:

| ID | Проверка |
|----|----------|
| `document_set_completeness` | Состав комплекта, дисциплины, индексация |
| `title_block_completeness` | Титульные листы и штампы |
| `stamp_quality` | Качество OCR штампов |
| `missing_source_data` | Полнота исходных данных |
| `ntd_references` | Ссылки на НТД |
| `requirements_traceability` | Трассировка требований |
| `interdisciplinary_refs` | Междисциплинарные ссылки |

```bash
# Список проверок
curl http://127.0.0.1:8100/projects/PTE-25-450/checks

# Запуск всех проверок
curl -X POST http://127.0.0.1:8100/projects/PTE-25-450/checks/run \
  -H 'Content-Type: application/json' -d '{}'

# Markdown-отчёт
curl http://127.0.0.1:8100/projects/PTE-25-450/checks/{run_id}/report.md

# Реестр требований и трассировка
curl http://127.0.0.1:8100/projects/PTE-25-450/requirements
curl -X POST http://127.0.0.1:8100/requirements/{id}/trace
```

Миграция: `make migrate` (таблица `check_runs`).

## Sprint 3

- Рендер PDF-листов в PNG (PyMuPDF), определение формата A0–A4
- Зоны: штамп, примечания, спецификация, поле чертежа
- OCR (Tesseract) по зонам, разбор штампа (лист, ревизия)
- Коллекция Qdrant `project_drawings_text`
- Preview API с bbox:
  - `GET /documents/{id}/pages/{n}/preview`
  - `GET /documents/{id}/pages/{n}/preview/image?highlight=true&token_id=...`
  - `POST /search/drawings`

```bash
pip install -e ".[drawings]"   # pymupdf + pytesseract
# macOS: brew install tesseract tesseract-lang
```

## Sprint 2

- Парсеры: **Docling → Unstructured → pypdf** (`packages/rag_parsers/factory.py`)
- Инженерная токенизация: разделы, таблицы, требования, НТД, стадия/дисциплина/ревизия, parent-child
- **Dense + sparse** векторы, **hybrid RRF** в Qdrant, **rerank**
- API: `POST /search/hybrid`, `/search/by-requirement`, `/search/by-ntd`
- Автозапись сущностей `Requirement` при индексации

```bash
pip install -e ".[parsers,embeddings]"   # опционально
```

## Roadmap (из ТЗ)

| Sprint | Содержание |
|--------|------------|
| **1** | Docker, upload, PDF parse (pypdf), tokens, dense index, search/query |
| **2** | Docling, headings, tables, requirements, NTD, hybrid fusion |
| **3** | Чертежи: OCR, штамп, bbox |
| **4** | AI-NK checks, requirements traceability |
| **5** | Пилот ИТЦ, LLM-ответы, Admin UI, evaluation |

## Переменные

См. `.env.example`.

## Тесты

```bash
make test
```
