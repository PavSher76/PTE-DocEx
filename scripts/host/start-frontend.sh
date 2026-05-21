#!/usr/bin/env bash
# Frontend (Vite) на http://127.0.0.1:5173

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=_common.sh
source "${SCRIPT_DIR}/_common.sh"

ROOT="$(pte_repo_root)"
FRONTEND="${ROOT}/frontend"
export VITE_API_BASE_URL="${VITE_API_BASE_URL:-http://127.0.0.1:8000}"

pte_assert_prereqs --node
pte_banner "Frontend — http://127.0.0.1:5173"
echo "VITE_API_BASE_URL = ${VITE_API_BASE_URL}"
echo "Остановка: Ctrl+C"
echo ""

cd "${FRONTEND}"
exec npm run dev -- --host 127.0.0.1 --port 5173
