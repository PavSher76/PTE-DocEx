# Общие функции для запуска PTE-DocEx на хосте (macOS / Linux).
# Подключение: source "$(dirname "$0")/_common.sh"

set -euo pipefail

pte_repo_root() {
  local script_dir
  script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  (cd "${script_dir}/../.." && pwd)
}

pte_runtime_dir() {
  local root
  root="$(pte_repo_root)"
  mkdir -p "${root}/.pte-host"
  printf '%s\n' "${root}/.pte-host"
}

pte_import_env_file() {
  local path="$1"
  [[ -f "${path}" ]] || return 0
  set -a
  # shellcheck disable=SC1090
  source "${path}"
  set +a
}

pte_set_host_defaults() {
  local root="$1"
  pte_import_env_file "${root}/.env"

  export DATABASE_URL="${DATABASE_URL:-sqlite:///./storage/app.db}"
  export LANGUAGETOOL_URL="${LANGUAGETOOL_URL:-http://127.0.0.1:8010/v2/check}"
  export OLLAMA_BASE_URL="${OLLAMA_BASE_URL:-http://127.0.0.1:11434}"
  export OLLAMA_MODEL="${OLLAMA_MODEL:-llama3.1:8b}"
  export OLLAMA_TIMEOUT_SECONDS="${OLLAMA_TIMEOUT_SECONDS:-180}"
}

pte_python_exe() {
  local root="$1"
  local venv_py="${root}/backend/.venv/bin/python"
  if [[ -x "${venv_py}" ]]; then
    printf '%s\n' "${venv_py}"
    return 0
  fi
  if command -v python3 >/dev/null 2>&1; then
    command -v python3
    return 0
  fi
  echo "Python не найден. Выполните: ./scripts/host/setup-host.sh" >&2
  return 1
}

pte_command_exists() {
  command -v "$1" >/dev/null 2>&1
}

pte_banner() {
  printf '\n=== %s ===\n' "$1"
}

pte_assert_prereqs() {
  local need_node=0
  local need_docker=0
  for arg in "$@"; do
    case "${arg}" in
      --node) need_node=1 ;;
      --docker) need_docker=1 ;;
    esac
  done

  if ! pte_command_exists python3; then
    echo "В PATH нет python3. Установите Python 3.12+." >&2
    exit 1
  fi
  if [[ "${need_node}" -eq 1 ]] && ! pte_command_exists npm; then
    echo "В PATH нет npm. Установите Node.js 22+." >&2
    exit 1
  fi
  if [[ "${need_docker}" -eq 1 ]] && ! pte_command_exists docker; then
    echo "В PATH нет docker. Установите Docker или поднимите LanguageTool на :8010 вручную." >&2
    exit 1
  fi
}

pte_host_env_example_path() {
  local script_dir
  script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  printf '%s/host.env.example\n' "${script_dir}"
}

pte_ensure_dotenv() {
  local root="$1"
  local target="${root}/.env"
  [[ -f "${target}" ]] && return 0

  local host_example
  host_example="$(pte_host_env_example_path)"
  if [[ -f "${host_example}" ]]; then
    cp "${host_example}" "${target}"
    echo "Создан .env из scripts/host/host.env.example (значения для хоста)."
    return 0
  fi
  if [[ -f "${root}/.env.example" ]]; then
    cp "${root}/.env.example" "${target}"
    echo "Создан .env из .env.example — для хоста задайте OLLAMA_BASE_URL=http://127.0.0.1:11434" >&2
  fi
}

pte_write_pid() {
  local name="$1"
  local pid="$2"
  local runtime
  runtime="$(pte_runtime_dir)"
  printf '%s\n' "${pid}" >"${runtime}/${name}.pid"
}

pte_read_pid() {
  local name="$1"
  local runtime file pid
  runtime="$(pte_runtime_dir)"
  file="${runtime}/${name}.pid"
  [[ -f "${file}" ]] || return 1
  pid="$(tr -d '[:space:]' <"${file}")"
  [[ -n "${pid}" ]] || return 1
  if kill -0 "${pid}" 2>/dev/null; then
    printf '%s\n' "${pid}"
    return 0
  fi
  rm -f "${file}"
  return 1
}

pte_stop_pidfile() {
  local name="$1"
  local pid
  if pid="$(pte_read_pid "${name}" 2>/dev/null)"; then
    echo "  остановка ${name} (PID ${pid})"
    kill "${pid}" 2>/dev/null || true
    sleep 0.5
    kill -9 "${pid}" 2>/dev/null || true
    rm -f "$(pte_runtime_dir)/${name}.pid"
  fi
}

pte_stop_port_listeners() {
  local port="$1"
  local pids
  if ! pte_command_exists lsof; then
    return 0
  fi
  pids="$(lsof -ti "tcp:${port}" -sTCP:LISTEN 2>/dev/null || true)"
  [[ -n "${pids}" ]] || return 0
  echo "  :${port} — завершение процессов: ${pids//$'\n'/ }"
  # shellcheck disable=SC2086
  kill ${pids} 2>/dev/null || true
  sleep 0.3
  # shellcheck disable=SC2086
  kill -9 ${pids} 2>/dev/null || true
}
