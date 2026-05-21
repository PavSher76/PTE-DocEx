#!/usr/bin/env bash
# Пилот ИТЦ: bootstrap + ingest sample + полный прогон
set -euo pipefail

API="${RAG_API_URL:-http://127.0.0.1:8100}"
PROJECT_ID="${RAG_PILOT_PROJECT:-PTE-ITC-450}"

echo "=== Bootstrap пилота ==="
curl -fsS -X POST "${API}/pilot/bootstrap?project_id=${PROJECT_ID}" | python3 -m json.tool

echo "=== Ingest sample ==="
RAG_SAMPLE_PROJECT="${PROJECT_ID}" ./scripts/ingest-sample.sh

echo "=== Пилотный прогон ==="
curl -fsS -X POST "${API}/pilot/${PROJECT_ID}/run" \
  -H "Content-Type: application/json" \
  -d '{}' | python3 -m json.tool

echo "=== Готово. Admin UI: cd apps/admin-ui && npm run dev ==="
