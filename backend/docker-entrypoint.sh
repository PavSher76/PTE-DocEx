#!/bin/sh
set -e

if ! python -c "import fastapi" >/dev/null 2>&1; then
  echo "Installing Python dependencies..."
  pip install --no-cache-dir --upgrade pip
  pip install --no-cache-dir -r requirements.txt
fi

exec "$@"
