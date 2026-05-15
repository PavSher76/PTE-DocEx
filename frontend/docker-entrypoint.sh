#!/bin/sh
set -e

ROLLUP_VERSION=4.60.3

configure_npm_proxy() {
  if [ -n "$HTTP_PROXY" ]; then
    npm config set proxy "$HTTP_PROXY"
    npm config set https-proxy "${HTTPS_PROXY:-$HTTP_PROXY}"
  fi
}

install_dependencies() {
  if [ ! -f node_modules/.package-lock.json ] && [ ! -d node_modules/vite ]; then
    echo "Installing frontend dependencies..."
    configure_npm_proxy
    npm ci --include=optional
  fi
}

case "$(uname -m)" in
  x86_64) rollup_pkg="@rollup/rollup-linux-x64-musl" ;;
  aarch64|arm64) rollup_pkg="@rollup/rollup-linux-arm64-musl" ;;
  *)
    echo "Unsupported CPU architecture: $(uname -m)" >&2
    exit 1
    ;;
esac

rollup_dir="node_modules/${rollup_pkg#@}"

install_dependencies

if [ ! -d "$rollup_dir" ]; then
  echo "Installing Rollup native module ($rollup_pkg)..."
  configure_npm_proxy
  npm install "${rollup_pkg}@${ROLLUP_VERSION}" --no-save
fi

exec "$@"
