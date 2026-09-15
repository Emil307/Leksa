#!/usr/bin/env bash
# Stops ONLY the process listening on this instance's BACKEND_PORT.
# Never kills by executable name — that would take down parallel sessions.
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/_env.sh"

pids="$(lsof -ti "tcp:$BACKEND_PORT" -sTCP:LISTEN || true)"

if [[ -z "$pids" ]]; then
  echo "Nothing is listening on port $BACKEND_PORT"
  exit 0
fi

echo "$pids" | while read -r pid; do
  kill "$pid"
  echo "Stopped backend PID $pid (port $BACKEND_PORT)"
done
