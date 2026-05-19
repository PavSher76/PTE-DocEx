#!/usr/bin/env bash
# Остановка процессов PTE-DocEx на хосте (pid-файлы и порты 5173, 8000, 8010).

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=_common.sh
source "${SCRIPT_DIR}/_common.sh"

ROOT="$(pte_repo_root)"
pte_banner "Остановка PTE-DocEx на хосте"

pte_stop_pidfile backend
pte_stop_pidfile frontend

for port in 5173 8000; do
  pte_stop_port_listeners "${port}"
done

if pte_command_exists docker; then
  cd "${ROOT}"
  if docker compose version >/dev/null 2>&1; then
    docker compose stop languagetool 2>/dev/null || true
  fi
  docker stop pte-docex-languagetool 2>/dev/null || true
  pte_stop_port_listeners 8010
fi

echo "Готово."
