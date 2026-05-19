#!/usr/bin/env bash
# LanguageTool на порту 8010 (Docker Compose из корня репозитория).

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=_common.sh
source "${SCRIPT_DIR}/_common.sh"

ROOT="$(pte_repo_root)"
pte_assert_prereqs --docker
pte_banner "LanguageTool — http://127.0.0.1:8010"

cd "${ROOT}"
if docker compose version >/dev/null 2>&1; then
  docker compose up -d languagetool
  echo "LanguageTool запущен (docker compose). Логи: docker compose logs -f languagetool"
else
  docker run --rm -d --name pte-docex-languagetool -p 8010:8010 erikvl87/languagetool:latest
  echo "LanguageTool запущен (docker run). Остановка: docker stop pte-docex-languagetool"
fi
