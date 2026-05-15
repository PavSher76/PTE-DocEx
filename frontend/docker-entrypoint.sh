#!/bin/sh
set -e

ROLLUP_VERSION=4.60.3

case "$(uname -m)" in
  x86_64)
    rollup_pkg="@rollup/rollup-linux-x64-musl"
    ;;
  aarch64|arm64)
    rollup_pkg="@rollup/rollup-linux-arm64-musl"
    ;;
  *)
    echo "Unsupported CPU architecture: $(uname -m)" >&2
    exit 1
    ;;
esac

rollup_dir="node_modules/${rollup_pkg#@}"

if [ ! -d "$rollup_dir" ]; then
  echo "Missing Rollup native module ($rollup_dir), reinstalling dependencies..."
  npm ci --include=optional
fi

if [ ! -d "$rollup_dir" ]; then
  npm install "${rollup_pkg}@${ROLLUP_VERSION}" --no-save
fi

exec "$@"
