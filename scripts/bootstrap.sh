#!/usr/bin/env bash

set -Eeuo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_PATH="${PROJECT_ROOT}/.venv"
ALL_BROWSERS=false

if [[ "${1:-}" == "--all-browsers" ]]; then
  ALL_BROWSERS=true
elif [[ $# -gt 0 ]]; then
  echo "Usage: bash scripts/bootstrap.sh [--all-browsers]" >&2
  exit 2
fi

if command -v python3 >/dev/null 2>&1; then
  PYTHON_COMMAND=(python3)
elif command -v python >/dev/null 2>&1; then
  PYTHON_COMMAND=(python)
elif command -v py >/dev/null 2>&1; then
  PYTHON_COMMAND=(py)
else
  echo "Python 3.11 or newer was not found in PATH." >&2
  exit 1
fi

if [[ ! -x "${VENV_PATH}/bin/python" && ! -x "${VENV_PATH}/Scripts/python.exe" ]]; then
  "${PYTHON_COMMAND[@]}" -m venv "${VENV_PATH}"
fi

if [[ -x "${VENV_PATH}/Scripts/python.exe" ]]; then
  VENV_PYTHON="${VENV_PATH}/Scripts/python.exe"
else
  VENV_PYTHON="${VENV_PATH}/bin/python"
fi

"${VENV_PYTHON}" -m pip install --upgrade pip

cd "${PROJECT_ROOT}"
"${VENV_PYTHON}" -m pip install -e ".[dev]"

if [[ "${ALL_BROWSERS}" == true ]]; then
  "${VENV_PYTHON}" -m playwright install
else
  "${VENV_PYTHON}" -m playwright install chromium
fi

echo "Ready. Copy .env.example to .env and configure the test data."
