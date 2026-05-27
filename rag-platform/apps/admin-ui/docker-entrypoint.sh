#!/bin/sh
set -e

BUILD_MARKER=dist/.pte-built

configure_npm_proxy() {
  if [ -n "$HTTP_PROXY" ]; then
    npm config set proxy "$HTTP_PROXY"
    npm config set https-proxy "${HTTPS_PROXY:-$HTTP_PROXY}"
  fi
}

if [ ! -f "$BUILD_MARKER" ]; then
  echo "Installing and building RAG admin-ui..."
  configure_npm_proxy
  npm ci 2>/dev/null || npm install
  npm run build
  touch "$BUILD_MARKER"
fi

exec "$@"
