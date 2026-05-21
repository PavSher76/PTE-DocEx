#!/usr/bin/env bash
# Установка зависимостей backend (venv + pip) и frontend (npm) на хосте.
# Запуск из корня репозитория:
#   ./scripts/host/setup-host.sh
#   ./scripts/host/setup-host.sh --system   # macOS: brew install OCR/LibreOffice

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=_common.sh
source "${SCRIPT_DIR}/_common.sh"

INSTALL_SYSTEM=0
for arg in "$@"; do
  case "${arg}" in
    --system) INSTALL_SYSTEM=1 ;;
    -h | --help)
      echo "Использование: $0 [--system]"
      echo "  --system  Установить системные пакеты (macOS: Homebrew)"
      exit 0
      ;;
  esac
done

ROOT="$(pte_repo_root)"
pte_banner "PTE-DocEx — установка на хосте"
pte_assert_prereqs --node

BACKEND="${ROOT}/backend"
FRONTEND="${ROOT}/frontend"
VENV="${BACKEND}/.venv"

echo "Репозиторий: ${ROOT}"
echo "Python: $(command -v python3)"

if [[ ! -d "${VENV}" ]]; then
  echo "Создание venv в backend/.venv ..."
  python3 -m venv "${VENV}"
fi

"${VENV}/bin/python" -m pip install --upgrade pip
"${VENV}/bin/pip" install -r "${BACKEND}/requirements.txt"

mkdir -p "${BACKEND}/storage"
pte_ensure_dotenv "${ROOT}"

echo "npm install (frontend) ..."
(
  cd "${FRONTEND}"
  if [[ -f package-lock.json ]]; then
    npm ci
  else
    npm install
  fi
)

if [[ "${INSTALL_SYSTEM}" -eq 1 ]]; then
  "${SCRIPT_DIR}/install-system-deps.sh"
fi

echo ""
echo "Готово. Дальше:"
echo "  1) ollama serve  &&  ollama pull llama3.1:8b"
echo "  2) ./scripts/host/start-host.sh"
echo ""
echo "OCR и сравнение DOCX: ./scripts/host/install-system-deps.sh (или --system при setup)"
