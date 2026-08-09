#!/usr/bin/env bash

set -Eeuo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPORT_PATH="${PROJECT_ROOT}/reports/smoke-report.html"
PRIORITY="p0"
HEADED=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --priority)
      PRIORITY="${2:-}"
      shift 2
      ;;
    --headed)
      HEADED=true
      shift
      ;;
    -h|--help)
      echo "Usage: bash scripts/run-smoke.sh [--priority p0|p1|p2|all] [--headed]"
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      exit 2
      ;;
  esac
done

case "${PRIORITY}" in
  p0|p1|p2|all) ;;
  *)
    echo "Priority must be p0, p1, p2 or all." >&2
    exit 2
    ;;
esac

if [[ -x "${PROJECT_ROOT}/.venv/Scripts/python.exe" ]]; then
  VENV_PYTHON="${PROJECT_ROOT}/.venv/Scripts/python.exe"
elif [[ -x "${PROJECT_ROOT}/.venv/bin/python" ]]; then
  VENV_PYTHON="${PROJECT_ROOT}/.venv/bin/python"
else
  echo "Run 'bash scripts/bootstrap.sh' first." >&2
  exit 1
fi

if [[ "${HEADED}" == true ]]; then
  export E2E_HEADLESS=false
fi

PYTEST_ARGS=(-m pytest -v --html "${REPORT_PATH}" --self-contained-html)
if [[ "${PRIORITY}" != "all" ]]; then
  PYTEST_ARGS+=(-m "${PRIORITY}")
fi

cd "${PROJECT_ROOT}"
"${VENV_PYTHON}" "${PYTEST_ARGS[@]}"
