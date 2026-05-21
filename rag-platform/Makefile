# RAG Platform — локальная инфраструктура и Sprint 1 MVP

COMPOSE = docker compose -f infra/docker-compose.yml --env-file .env
ROOT := $(shell pwd)
export PYTHONPATH := $(ROOT)/packages:$(ROOT)/apps/api:$(ROOT)/apps/worker

.PHONY: up down logs migrate test ingest-sample query health install dev-api dev-worker dev-admin pilot-itc

install:
	python3 -m venv .venv
	.venv/bin/pip install -e ".[dev]"

up:
	$(COMPOSE) up -d postgres redis minio minio-init qdrant
	@echo "Инфраструктура поднята. API/worker: make up-all"

up-all:
	$(COMPOSE) up -d --build

down:
	$(COMPOSE) down

logs:
	$(COMPOSE) logs -f

migrate:
	.venv/bin/alembic upgrade head

test:
	.venv/bin/pytest -q

health:
	curl -s http://127.0.0.1:8100/health | python3 -m json.tool
	curl -s http://127.0.0.1:8100/health/ready | python3 -m json.tool

ingest-sample:
	./scripts/ingest-sample.sh

query:
	./scripts/query-sample.sh

dev-api:
	.venv/bin/uvicorn app.main:app --app-dir apps/api --host 127.0.0.1 --port 8100 --reload

dev-worker:
	.venv/bin/python -m app.worker

dev-admin:
	cd apps/admin-ui && npm install && npm run dev

pilot-itc:
	chmod +x scripts/pilot-itc.sh && ./scripts/pilot-itc.sh
