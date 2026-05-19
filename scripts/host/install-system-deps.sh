#!/usr/bin/env bash
# Системные зависимости для OCR и сравнения документов на хосте.

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=_common.sh
source "${SCRIPT_DIR}/_common.sh"

pte_banner "Системные зависимости (OCR / LibreOffice)"

OS="$(uname -s)"
case "${OS}" in
  Darwin)
    if ! pte_command_exists brew; then
      echo "Установите Homebrew: https://brew.sh" >&2
      exit 1
    fi
    echo "macOS: brew install libreoffice tesseract tesseract-lang poppler"
    brew install libreoffice tesseract tesseract-lang poppler
    ;;
  Linux)
    if pte_command_exists apt-get; then
      echo "Debian/Ubuntu — требуются права sudo:"
      echo "  sudo apt-get update"
      echo "  sudo apt-get install -y libreoffice tesseract-ocr tesseract-ocr-rus poppler-utils"
      if [[ "${EUID}" -eq 0 ]]; then
        apt-get update
        apt-get install -y libreoffice tesseract-ocr tesseract-ocr-rus poppler-utils
      else
        sudo apt-get update
        sudo apt-get install -y libreoffice tesseract-ocr tesseract-ocr-rus poppler-utils
      fi
    else
      echo "Установите вручную: LibreOffice, Tesseract (rus+eng), poppler-utils." >&2
      exit 1
    fi
    ;;
  *)
    echo "ОС ${OS}: установите LibreOffice, Tesseract и Poppler вручную." >&2
    exit 1
    ;;
esac

echo "Готово."
