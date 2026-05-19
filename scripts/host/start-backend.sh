#!/usr/bin/env bash
# Backend (FastAPI) на http://127.0.0.1:8000

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=_common.sh
source "${SCRIPT_DIR}/_common.sh"

ROOT="$(pte_repo_root)"
pte_set_host_defaults "${ROOT}"
PYTHON="$(pte_python_exe "${ROOT}")"
BACKEND="${ROOT}/backend"

mkdir -p "${BACKEND}/storage"
pte_banner "Backend — http://127.0.0.1:8000"
echo "LanguageTool: ${LANGUAGETOOL_URL}"
echo "Ollama:       ${OLLAMA_BASE_URL}"
echo "БД:           ${DATABASE_URL}"
echo "Остановка: Ctrl+C"
echo ""

cd "${BACKEND}"
exec "${PYTHON}" -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
