#!/usr/bin/env bash

set -Eeuo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [[ -x "${PROJECT_ROOT}/.venv/Scripts/python.exe" ]]; then
  PYTHON="${PROJECT_ROOT}/.venv/Scripts/python.exe"
else
  PYTHON="${PROJECT_ROOT}/.venv/bin/python"
fi

cd "${PROJECT_ROOT}"
"${PYTHON}" scripts/publish_live_data.py "$@"
