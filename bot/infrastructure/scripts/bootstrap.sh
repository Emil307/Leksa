#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INFRA_DIR="$(dirname "$SCRIPT_DIR")"
BOT_DIR="$(dirname "$INFRA_DIR")"
PYTHON_BIN="${PYTHON_BIN:-python3.12}"

if [[ ! -f "$INFRA_DIR/.env" ]]; then
  "$SCRIPT_DIR/setup-ports.sh"
fi

if [[ ! -d "$BOT_DIR/.venv" ]]; then
  "$PYTHON_BIN" -m venv "$BOT_DIR/.venv"
fi

"$BOT_DIR/.venv/bin/python" -m pip install --upgrade pip
"$BOT_DIR/.venv/bin/python" -m pip install -r "$BOT_DIR/requirements.txt"
"$BOT_DIR/.venv/bin/python" -m pip check
