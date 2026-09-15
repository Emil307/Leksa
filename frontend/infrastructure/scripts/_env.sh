#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INFRA_DIR="$(dirname "$SCRIPT_DIR")"
FRONTEND_DIR="$(dirname "$INFRA_DIR")"
LOCAL_ENV="$INFRA_DIR/.env"
APP_ENV="$FRONTEND_DIR/.env.local"

if [[ ! -f "$LOCAL_ENV" ]]; then
  echo "Missing $LOCAL_ENV. Run $SCRIPT_DIR/setup-ports.sh first." >&2
  exit 1
fi

if [[ ! -f "$APP_ENV" ]]; then
  echo "Missing $APP_ENV. Create it from $FRONTEND_DIR/.env.example and set VITE_API_URL." >&2
  exit 1
fi

set -a
source "$LOCAL_ENV"
set +a

app_url() {
  echo "http://${FRONTEND_EXTERNAL_HOST}:${FRONTEND_PORT}"
}

stub_url() {
  echo "http://localhost:${E2E_API_STUB_PORT}"
}
