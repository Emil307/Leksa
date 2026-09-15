#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/_env.sh"

RUN_DIR="$INFRA_DIR/run"
PID_FILE="$RUN_DIR/bot.pid"
mkdir -p "$RUN_DIR"

if [[ -f "$PID_FILE" ]] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
  echo "Bot is already running with PID $(cat "$PID_FILE")." >&2
  exit 1
fi

export DB_HOST=127.0.0.1
export DB_PORT="$BOT_DB_PORT"
export REDIS_HOST=127.0.0.1
export REDIS_PORT="$BOT_REDIS_PORT"
export PYTHONPATH="$BOT_DIR/src"

cd "$(dirname "$BOT_DIR")"
bot_python="$(python_bin)"
"$bot_python" -m dotenv -f "$BOT_ENV" run --no-override -- \
  "$bot_python" -m uvicorn presentation.bot.main:app \
    --host "$BOT_HOST" \
    --port "$BOT_PORT" &
bot_pid=$!
echo "$bot_pid" > "$PID_FILE"

cleanup() {
  rm -f "$PID_FILE"
}
trap cleanup EXIT INT TERM
wait "$bot_pid"
