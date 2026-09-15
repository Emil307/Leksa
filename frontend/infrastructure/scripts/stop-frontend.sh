#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/_env.sh"

PID_FILE="$INFRA_DIR/run/frontend.pid"

if [[ ! -f "$PID_FILE" ]]; then
  echo "Frontend is not running (no PID file)."
  exit 0
fi

frontend_pid="$(cat "$PID_FILE")"
if kill -0 "$frontend_pid" 2>/dev/null; then
  pkill -TERM -P "$frontend_pid" 2>/dev/null || true
  kill "$frontend_pid" 2>/dev/null || true
fi
rm -f "$PID_FILE"
echo "Frontend stopped."
