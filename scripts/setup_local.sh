#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

if ! command -v uv >/dev/null 2>&1; then
  echo "uv is required but not installed." >&2
  exit 1
fi

if [[ -f "${HOME}/.cargo/env" ]]; then
  # shellcheck disable=SC1090
  source "${HOME}/.cargo/env"
fi

if ! command -v cargo >/dev/null 2>&1; then
  echo "cargo not found; installing Rust toolchain via rustup."
  curl https://sh.rustup.rs -sSf | sh -s -- -y --profile minimal --no-modify-path
  # shellcheck disable=SC1090
  source "${HOME}/.cargo/env"
fi

uv venv .venv
uv pip install --python .venv/bin/python maturin pytest
(
  cd amm_sim_rs
  ../.venv/bin/maturin develop --release
)
uv pip install --python .venv/bin/python -e '.[dev]'

git config core.hooksPath .githooks

echo "Local setup complete."
echo "Activate with: source .venv/bin/activate"
echo "Protected mechanics hooks are active via core.hooksPath=.githooks"
