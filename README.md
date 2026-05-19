# PTE DocEx

Локальный MVP веб-системы для контроля исходящей переписки, комплектов документации, контекста инвестиционно-строительного проекта и анализа сессий выученных уроков.

## Модули

### Переписка

- загрузка PDF исходящего письма;
- извлечение текста через PyMuPDF или OCR для сканов;
- проверка через LanguageTool;
- фильтрация ложных срабатываний и оценка стиля через локальную Ollama-модель;
- итоговый статус: `OK`, `Требует проверки`, `Критично`.

### Документация

- сравнение PDF с редактируемым DOCX, ODT или RTF;
- пакетная загрузка PDF с проверкой встроенной УКЭП (63-ФЗ);
- постраничное сравнение текста и заключение об идентичности.

### Контекст проекта

- datacentric-профили инвестиционно-строительного проекта;
- экспорт JSON-контекста для LLM и XML «Задание на проектирование» (Минстрой 01.00).

### Выученные уроки с ИИ

- загрузка формы «Форма для подготовки к сессии ВУ» (`.xlsm`, `.xlsx`, `.xls`);
- автоматический разбор метаданных проекта, разделов и строк уроков в JSON;
- выбор модели Ollama из списка доступных на хосте;
- анализ корневых причин и системных рекомендаций по промпту.

## Требования

| Компонент | Docker-режим | Режим на хосте |
|-----------|--------------|----------------|
| Docker Desktop / Docker Engine | да | опционально (для LanguageTool) |
| Ollama на хосте | да | да |
| Python 3.12+ | в контейнере | да (backend) |
| Node.js 22+ | в контейнере | да (frontend) |
| LibreOffice, Tesseract, Poppler | в контейнере* | да (для OCR и сравнения документов) |

\* По умолчанию в `docker-compose.yml` задано `SKIP_APT_PACKAGES=1` — образ backend собирается без LibreOffice/Tesseract. Для полного OCR и сравнения документов в Docker установите `SKIP_APT_PACKAGES=0` и пересоберите backend.

---

## Запуск в Docker (рекомендуется)

### 1. Подготовка Ollama

Ollama должна работать **на хосте**, не в контейнере:

```bash
ollama pull llama3.1:8b
ollama serve
```

Проверка:

```bash
curl http://127.0.0.1:11434/api/tags
```

### 2. Переменные окружения

```bash
cp .env.example .env
```

Для Docker Desktop на macOS/Windows обычно достаточно значений по умолчанию:

```env
OLLAMA_BASE_URL=http://host.docker.internal:11434
OLLAMA_MODEL=llama3.1:8b
```

### 3. Права на entrypoint-скрипты

Volume `./frontend:/app` монтирует `docker-entrypoint.sh` с хоста. Файл должен быть исполняемым:

```bash
chmod +x frontend/docker-entrypoint.sh backend/docker-entrypoint.sh
```

Без этого frontend может завершиться с ошибкой `permission denied`.

### 4. Старт всех сервисов

```bash
docker compose up --build
```

В фоне:

```bash
docker compose up --build -d
```

### 5. Проверка

| Сервис | URL | Команда проверки |
|--------|-----|------------------|
| Frontend | http://localhost:5173 | открыть в браузере |
| Backend | http://localhost:8000 | `curl http://localhost:8000/health` |
| LanguageTool | http://localhost:8010 | в составе backend |
| Ollama (хост) | http://127.0.0.1:11434 | `curl http://localhost:8000/api/learned-lessons/models` |

Статус контейнеров:

```bash
docker compose ps
```

Перезапуск одного сервиса:

```bash
docker compose restart backend
docker compose restart frontend
```

Остановка:

```bash
docker compose down
```

### Состав контейнеров

- **backend** — FastAPI, порт `8000`; при старте синхронизирует Python-зависимости из `requirements.txt`;
- **frontend** — Vite + React, порт `5173`; проксирует `/api` на backend;
- **languagetool** — сервис проверки орфографии, порт `8010`.

Backend обращается к Ollama через `host.docker.internal:11434` (настроено в `docker-compose.yml` через `extra_hosts`).

---

## Запуск на хосте (без Docker для приложения)

Подходит для разработки backend/frontend. LanguageTool поднимается отдельным контейнером; Ollama — на хосте.

### Быстрый старт (скрипты)

**macOS / Linux** (из корня репозитория):

```bash
chmod +x scripts/host/*.sh

# 1) Установка venv, npm и .env для хоста
./scripts/host/setup-host.sh
# Опционально: системные пакеты OCR/LibreOffice (macOS — Homebrew)
./scripts/host/setup-host.sh --system

# 2) Ollama на хосте
ollama pull llama3.1:8b
ollama serve

# 3) Запуск LanguageTool + backend + frontend
./scripts/host/start-host.sh
# Или frontend в текущем терминале:
./scripts/host/start-host.sh --foreground

# Проверка и остановка
./scripts/host/check-host.sh
./scripts/host/stop-host.sh
```

Через **Make**:

```bash
make setup-host
make start-host
make check-host
make stop-host
```

**Windows (PowerShell):**

```powershell
.\scripts\powershell\Setup-Host.ps1
.\scripts\powershell\Start-Host.ps1
.\scripts\powershell\Stop-Host.ps1
```

Скрипты создают `.env` из `scripts/host/host.env.example` (`OLLAMA_BASE_URL=http://127.0.0.1:11434`, `LANGUAGETOOL_URL=http://127.0.0.1:8010/v2/check`). Логи фоновых процессов: `.pte-host/backend.log`, `.pte-host/frontend.log`.

| Скрипт | Назначение |
|--------|------------|
| `scripts/host/setup-host.sh` | venv + pip, `npm ci`, `.env`, `backend/storage` |
| `scripts/host/install-system-deps.sh` | LibreOffice, Tesseract, Poppler |
| `scripts/host/start-host.sh` | LT (Docker) + backend + frontend |
| `scripts/host/start-{backend,frontend,languagetool}.sh` | Отдельный сервис |
| `scripts/host/stop-host.sh` | Остановка по pid и портам |
| `scripts/host/check-host.sh` | Проверка Ollama, LT, API, UI |

Интерфейс: http://127.0.0.1:5173

### Ручной запуск (без скриптов)

<details>
<summary>Шаги вручную</summary>

#### Ollama

```bash
ollama pull llama3.1:8b
ollama serve
```

#### LanguageTool

```bash
docker compose up -d languagetool
```

#### Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export OLLAMA_BASE_URL=http://127.0.0.1:11434
export LANGUAGETOOL_URL=http://127.0.0.1:8010/v2/check
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

#### Frontend

```bash
cd frontend && npm ci
VITE_API_BASE_URL=http://127.0.0.1:8000 npm run dev
```

</details>

### Проверка

```bash
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/api/learned-lessons/models
./scripts/host/check-host.sh
```

---

## Переменные окружения

| Переменная | Описание | Docker | Хост |
|------------|----------|--------|------|
| `OLLAMA_BASE_URL` | Адрес Ollama API | `http://host.docker.internal:11434` | `http://127.0.0.1:11434` |
| `OLLAMA_MODEL` | Модель по умолчанию | `llama3.1:8b` | `llama3.1:8b` |
| `OLLAMA_TIMEOUT_SECONDS` | Таймаут запросов к Ollama | `180` | `180` |
| `LANGUAGETOOL_URL` | URL LanguageTool | `http://languagetool:8010/v2/check` | `http://127.0.0.1:8010/v2/check` |
| `LANGUAGETOOL_LANGUAGE` | Язык проверки | `ru-RU` | `ru-RU` |
| `OCR_LANGUAGE` | Языки Tesseract | `rus+eng` | `rus+eng` |
| `OCR_DPI` | DPI рендера PDF для OCR | `300` | `300` |
| `SKIP_APT_PACKAGES` | Пропустить LibreOffice/Tesseract в образе backend | `1` | — |
| `NO_PROXY` | Исключения для прокси (важно для Ollama) | `localhost,127.0.0.1,host.docker.internal,.local` | — |

Полный список — в `.env.example`.

### Корпоративная сеть

Если используется HTTP-прокси, скопируйте настройки из `docker/proxy.env.example` в `.env`. В `NO_PROXY` обязательно включите `host.docker.internal`, иначе backend не достучится до Ollama на хосте.

```bash
docker compose -f docker-compose.yml -f docker-compose.corp-network.yml up --build
```

---

## API (примеры)

### Проверка переписки (PDF)

```bash
curl -X POST http://localhost:8000/api/correspondence/check-pdf \
  -F "pdf_file=@letter.pdf" \
  -F "strictness=strict" \
  -F "business_context=Исходящее письмо подрядчику" \
  -F "check_prompt=Проверь письмо и замечания LanguageTool. Верни JSON."
```

### Сравнение документов

```bash
curl -X POST http://localhost:8000/api/documents/compare \
  -F "pdf_file=@document.pdf" \
  -F "editable_file=@document.docx"
```

### Выученные уроки — список моделей Ollama

```bash
curl http://localhost:8000/api/learned-lessons/models
```

### Выученные уроки — анализ формы ВУ

```bash
curl -X POST http://localhost:8000/api/learned-lessons/analyze \
  -F "excel_file=@Форма для подготовки к сессии ВУ.xlsm" \
  -F "ollama_model=llama3.1:8b" \
  -F "analysis_prompt=Ты эксперт управления проектами. Рассмотри данные сессии выученные уроки и выяви корневые причины указанных проект в проекте. Дай рекомендации по системному устранению корневых причин."
```

---

## Устранение неполадок

### Frontend: `permission denied` на `docker-entrypoint.sh`

```bash
chmod +x frontend/docker-entrypoint.sh
docker compose up -d frontend
```

### Backend не стартует: `No module named 'openpyxl'`

Backend при каждом запуске синхронизирует зависимости. Пересоздайте контейнер:

```bash
docker compose up -d --build backend
```

### Список моделей Ollama пустой

1. Убедитесь, что Ollama запущена на хосте: `curl http://127.0.0.1:11434/api/tags`
2. Проверьте `OLLAMA_BASE_URL` в `.env` — для Docker это `http://host.docker.internal:11434`
3. Если задан `HTTP_PROXY`, добавьте `host.docker.internal` в `NO_PROXY`
4. Проверьте API: `curl http://localhost:8000/api/learned-lessons/models`

### Backend не отвечает (таймаут на :8000)

```bash
docker compose logs backend --tail 50
docker compose ps
```

### OCR / сравнение документов не работает в Docker

Установите `SKIP_APT_PACKAGES=0` в `.env` или переменных окружения и пересоберите backend:

```bash
SKIP_APT_PACKAGES=0 docker compose up --build backend
```

---

## Ограничения MVP

- Single-user локальный режим без ролей и аудита.
- OCR-сравнение даёт вероятностное заключение с процентом совпадения.
- Большие документы обрабатываются синхронно и могут занимать несколько минут.
- Очереди задач и расширенные форматы документов — в следующих версиях.
