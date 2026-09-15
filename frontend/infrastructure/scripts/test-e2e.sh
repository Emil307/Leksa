#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/_env.sh"

E2E_DIR="$FRONTEND_DIR/e2e"
export APP_URL="${APP_URL:-$(app_url)}"
export E2E_HEADLESS="${E2E_HEADLESS:-true}"
export E2E_API_STUB_PORT="${E2E_API_STUB_PORT:?Missing E2E_API_STUB_PORT in $LOCAL_ENV. Re-run $SCRIPT_DIR/setup-ports.sh with FORCE=1.}"

if ! curl -sf -o /dev/null "$APP_URL"; then
  echo "Frontend is not reachable at $APP_URL. Start it with $SCRIPT_DIR/run-frontend.sh first." >&2
  exit 1
fi

if [[ "$(cat "$INFRA_DIR/run/frontend.api-url" 2>/dev/null)" != "$(stub_url)" ]]; then
  echo "Dev server at $APP_URL is not pointed at the API stub $(stub_url). Restart it with E2E_STUB=1 $SCRIPT_DIR/run-frontend.sh." >&2
  exit 1
fi

cd "$E2E_DIR"
if [[ $# -gt 0 ]]; then
  ./gradlew test --tests "$1" --rerun
else
  ./gradlew test --rerun
fi
