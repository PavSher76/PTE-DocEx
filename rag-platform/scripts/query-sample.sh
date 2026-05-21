#!/usr/bin/env bash
set -euo pipefail

API="${RAG_API_URL:-http://127.0.0.1:8100}"
PROJECT_ID="${RAG_SAMPLE_PROJECT:-PTE-25-450}"
QUERY="${1:-Какие исходные данные требуются для раздела ТХ?}"

curl -fsS -X POST "${API}/query" \
  -H "Content-Type: application/json" \
  -d "$(python3 - <<PY
import json
print(json.dumps({
  "project_id": "${PROJECT_ID}",
  "query": """${QUERY}""",
  "filters": {"stage": "PD", "discipline": "TX"},
  "top_k": 5,
  "debug": True,
}))
PY
)" | python3 -m json.tool
