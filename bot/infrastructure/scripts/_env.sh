#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INFRA_DIR="$(dirname "$SCRIPT_DIR")"
BOT_DIR="$(dirname "$INFRA_DIR")"
LOCAL_ENV="$INFRA_DIR/.env"
BOT_ENV="$BOT_DIR/.env"
COMPOSE_FILE="$INFRA_DIR/docker-compose.yml"

if [[ ! -f "$LOCAL_ENV" ]]; then
  echo "Missing $LOCAL_ENV. Run $SCRIPT_DIR/setup-ports.sh first." >&2
  exit 1
fi

if [[ ! -f "$BOT_ENV" ]]; then
  echo "Missing $BOT_ENV. Create it from $BOT_DIR/.env.example and add real secrets." >&2
  exit 1
fi

set -a
source "$LOCAL_ENV"
set +a

compose() {
  docker compose --env-file "$LOCAL_ENV" -f "$COMPOSE_FILE" "$@"
}

python_bin() {
  if [[ -x "$BOT_DIR/.venv/bin/python" ]]; then
    echo "$BOT_DIR/.venv/bin/python"
  else
    echo "python3.12"
  fi
}
