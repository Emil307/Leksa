#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/_env.sh"

PID_FILE="$INFRA_DIR/run/bot.pid"

if [[ ! -f "$PID_FILE" ]]; then
  echo "Bot is not running (no PID file)."
  exit 0
fi

bot_pid="$(cat "$PID_FILE")"
if kill -0 "$bot_pid" 2>/dev/null; then
  kill "$bot_pid"
fi
rm -f "$PID_FILE"
