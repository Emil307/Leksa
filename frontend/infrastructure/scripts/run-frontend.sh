#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/_env.sh"

RUN_DIR="$INFRA_DIR/run"
LOG_DIR="$INFRA_DIR/logs"
PID_FILE="$RUN_DIR/frontend.pid"
mkdir -p "$RUN_DIR" "$LOG_DIR"

if [[ -f "$PID_FILE" ]] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
  echo "Frontend is already running with PID $(cat "$PID_FILE")." >&2
  exit 1
fi

if [[ ! -d "$FRONTEND_DIR/node_modules" ]]; then
  (cd "$FRONTEND_DIR" && npm install --no-audit --no-fund)
fi

if [[ "${E2E_STUB:-0}" == "1" ]]; then
  export VITE_API_URL="$(stub_url)"
fi

cd "$FRONTEND_DIR"
npm run dev -- --host "$FRONTEND_HOST" --port "$FRONTEND_PORT" --strictPort \
  > "$LOG_DIR/frontend.log" 2>&1 &
frontend_pid=$!
echo "$frontend_pid" > "$PID_FILE"
echo "${VITE_API_URL:-}" > "$RUN_DIR/frontend.api-url"
echo "Frontend dev server starting with PID $frontend_pid at $(app_url) (log: $LOG_DIR/frontend.log)"

cleanup() {
  rm -f "$PID_FILE" "$RUN_DIR/frontend.api-url"
}
trap cleanup EXIT INT TERM
wait "$frontend_pid"
