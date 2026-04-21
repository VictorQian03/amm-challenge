#!/usr/bin/env bash
set -euo pipefail

if [[ "${1:-}" == "" ]]; then
  echo "hook mode is required" >&2
  exit 2
fi

ROOT_DIR="$(git rev-parse --show-toplevel)"
cd "${ROOT_DIR}"

if [[ -x "${ROOT_DIR}/.venv/bin/python" ]]; then
  exec "${ROOT_DIR}/.venv/bin/python" -m amm_competition.competition.protected_surface --mode "$1"
fi

if command -v uv >/dev/null 2>&1; then
  exec uv run python -m amm_competition.competition.protected_surface --mode "$1"
fi

echo "Unable to run protected mechanics checker: install the repo environment first." >&2
exit 1
