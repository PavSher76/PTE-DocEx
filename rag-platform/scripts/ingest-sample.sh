#!/usr/bin/env bash
set -euo pipefail

API="${RAG_API_URL:-http://127.0.0.1:8100}"
PROJECT_ID="${RAG_SAMPLE_PROJECT:-PTE-25-450}"
SAMPLE="${1:-data/samples/sample.txt}"

if [[ ! -f "${SAMPLE}" ]]; then
  mkdir -p "$(dirname "${SAMPLE}")"
  cat >"${SAMPLE}" <<'EOF'
Раздел ТХ. Исходные данные.
Объект должен быть спроектирован в соответствии с СП 60.13330.
Стадия: ПД. Код документа: ПЗ-ТХ.
EOF
fi

curl -fsS -X POST "${API}/projects" \
  -H "Content-Type: application/json" \
  -d "{\"project_id\":\"${PROJECT_ID}\",\"name\":\"Пилот RAG\",\"description\":\"Sample\"}" \
  >/dev/null 2>&1 || true

echo "Загрузка ${SAMPLE} ..."
RESP=$(curl -fsS -X POST "${API}/documents/upload" \
  -F "project_id=${PROJECT_ID}" \
  -F "file=@${SAMPLE}" \
  -F "stage=PD" \
  -F "discipline=TX" \
  -F "document_code=ПЗ-ТХ")

echo "${RESP}" | python3 -m json.tool
DOC_ID=$(echo "${RESP}" | python3 -c "import sys,json; print(json.load(sys.stdin)['document_id'])")

echo "Ожидание индексации ..."
for _ in $(seq 1 30); do
  STATUS=$(curl -fsS "${API}/documents/${DOC_ID}/status")
  echo "${STATUS}" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['job']['status'], 'tokens=', d['tokens_count'])"
  STATE=$(echo "${STATUS}" | python3 -c "import sys,json; print(json.load(sys.stdin)['job']['status'])")
  if [[ "${STATE}" == "indexed" ]]; then
    break
  fi
  if [[ "${STATE}" == "failed" ]]; then
    echo "${STATUS}" | python3 -m json.tool
    exit 1
  fi
  sleep 2
done
