#!/bin/sh
set -e

echo "Syncing Python dependencies..."
pip install --no-cache-dir --upgrade pip
pip install --no-cache-dir -r requirements.txt

exec "$@"
