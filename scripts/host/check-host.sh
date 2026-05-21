#!/usr/bin/env bash
# Проверка готовности локального окружения.

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=_common.sh
source "${SCRIPT_DIR}/_common.sh"

ROOT="$(pte_repo_root)"
pte_set_host_defaults "${ROOT}"

pte_banner "Проверка окружения"

ok() { echo "  [ok] $1"; }
warn() { echo "  [!!] $1"; }
fail() { echo "  [xx] $1"; }

pte_command_exists python3 && ok "python3: $(command -v python3)" || fail "python3 не найден"
pte_command_exists npm && ok "npm: $(command -v npm)" || fail "npm не найден"
[[ -x "${ROOT}/backend/.venv/bin/python" ]] && ok "backend/.venv" || warn "нет backend/.venv — выполните setup-host.sh"
[[ -d "${ROOT}/frontend/node_modules" ]] && ok "frontend/node_modules" || warn "нет node_modules — выполните setup-host.sh"
[[ -f "${ROOT}/.env" ]] && ok ".env" || warn "нет .env — будет создан при setup-host.sh"

if curl -fsS --max-time 2 "${OLLAMA_BASE_URL}/api/tags" >/dev/null 2>&1; then
  ok "Ollama ${OLLAMA_BASE_URL}"
else
  warn "Ollama недоступна (${OLLAMA_BASE_URL}) — ollama serve"
fi

LT_BASE="${LANGUAGETOOL_URL%/v2/check}"
if curl -fsS --max-time 2 "${LT_BASE}/v2/languages" >/dev/null 2>&1; then
  ok "LanguageTool ${LT_BASE}"
else
  warn "LanguageTool недоступен — ./scripts/host/start-languagetool.sh"
fi

if curl -fsS --max-time 2 "http://127.0.0.1:8000/health" >/dev/null 2>&1; then
  ok "Backend http://127.0.0.1:8000/health"
else
  warn "Backend не отвечает на :8000"
fi

if curl -fsS --max-time 2 "http://127.0.0.1:5173" >/dev/null 2>&1; then
  ok "Frontend http://127.0.0.1:5173"
else
  warn "Frontend не отвечает на :5173"
fi

for cmd in tesseract libreoffice pdftoppm; do
  if pte_command_exists "${cmd}"; then
    ok "${cmd}"
  else
    warn "${cmd} не в PATH (OCR/сравнение DOCX)"
  fi
done

echo ""
