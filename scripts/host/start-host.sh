#!/usr/bin/env bash
# Запуск LanguageTool, backend и frontend на хосте.
#   ./scripts/host/start-host.sh              # сервисы в фоне, логи в .pte-host/
#   ./scripts/host/start-host.sh --foreground # frontend на переднем плане
#   ./scripts/host/start-host.sh --skip-lt    # без LanguageTool

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=_common.sh
source "${SCRIPT_DIR}/_common.sh"

SKIP_LT=0
FOREGROUND=0
SKIP_SETUP_CHECK=0

for arg in "$@"; do
  case "${arg}" in
    --skip-lt | --skip-languagetool) SKIP_LT=1 ;;
    --foreground | -f) FOREGROUND=1 ;;
    --skip-setup-check) SKIP_SETUP_CHECK=1 ;;
    -h | --help)
      cat <<'EOF'
Использование: start-host.sh [опции]

  --foreground, -f     Frontend в текущем терминале (backend и LT — в фоне)
  --skip-lt            Не запускать LanguageTool
  --skip-setup-check   Не вызывать setup-host при отсутствии venv/node_modules
EOF
      exit 0
      ;;
  esac
done

ROOT="$(pte_repo_root)"
RUNTIME="$(pte_runtime_dir)"
VENV_PY="${ROOT}/backend/.venv/bin/python"
NODE_MODULES="${ROOT}/frontend/node_modules"

pte_banner "PTE-DocEx — запуск на хосте"

if [[ "${SKIP_SETUP_CHECK}" -eq 0 ]]; then
  if [[ ! -x "${VENV_PY}" ]] || [[ ! -d "${NODE_MODULES}" ]]; then
    echo "Не найдены backend/.venv или frontend/node_modules — запуск setup-host.sh ..."
    "${SCRIPT_DIR}/setup-host.sh"
  fi
fi

pte_ensure_dotenv "${ROOT}"
pte_set_host_defaults "${ROOT}"

start_languagetool() {
  if [[ "${SKIP_LT}" -eq 1 ]]; then
    echo "LanguageTool пропущен (--skip-lt)."
    return 0
  fi
  if ! pte_command_exists docker; then
    echo "Docker не найден — LanguageTool не запущен. Нужен сервис на :8010." >&2
    return 0
  fi
  echo "  + LanguageTool :8010"
  "${SCRIPT_DIR}/start-languagetool.sh" >/dev/null
  sleep 2
}

start_backend_bg() {
  local log="${RUNTIME}/backend.log"
  if pte_read_pid backend >/dev/null 2>&1; then
    echo "  backend уже запущен (PID $(pte_read_pid backend))"
    return 0
  fi
  echo "  + Backend :8000 (лог: ${log})"
  (
    # shellcheck source=_common.sh
    source "${SCRIPT_DIR}/_common.sh"
    pte_set_host_defaults "${ROOT}"
    cd "${ROOT}/backend"
    nohup "${VENV_PY}" -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload >>"${log}" 2>&1 &
    echo $! >"${RUNTIME}/backend.pid"
  )
  sleep 1
}

start_frontend_bg() {
  local log="${RUNTIME}/frontend.log"
  if pte_read_pid frontend >/dev/null 2>&1; then
    echo "  frontend уже запущен (PID $(pte_read_pid frontend))"
    return 0
  fi
  echo "  + Frontend :5173 (лог: ${log})"
  (
    cd "${ROOT}/frontend"
    export VITE_API_BASE_URL="${VITE_API_BASE_URL:-http://127.0.0.1:8000}"
    nohup npm run dev -- --host 127.0.0.1 --port 5173 >>"${log}" 2>&1 &
    echo $! >"${RUNTIME}/frontend.pid"
  )
  sleep 2
}

start_languagetool
start_backend_bg

if [[ "${FOREGROUND}" -eq 1 ]]; then
  echo ""
  echo "Откройте: http://127.0.0.1:5173"
  echo "Остановка backend/LT после выхода: ./scripts/host/stop-host.sh"
  echo ""
  exec "${SCRIPT_DIR}/start-frontend.sh"
fi

start_frontend_bg

echo ""
echo "Сервисы запущены:"
echo "  UI:      http://127.0.0.1:5173"
echo "  API:     http://127.0.0.1:8000/health"
echo "  Логи:    ${RUNTIME}/backend.log  ${RUNTIME}/frontend.log"
echo ""
echo "На хосте должен работать Ollama: ollama serve && ollama pull ${OLLAMA_MODEL:-llama3.1:8b}"
echo "Остановка: ./scripts/host/stop-host.sh"
