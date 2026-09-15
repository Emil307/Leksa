#!/usr/bin/env bash
# Runs the black-box acceptance suite against the already-running stack.
# Extra arguments are passed to pytest, e.g.:
#   test-acceptance.sh -k TestHealthAcceptance
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/_env.sh"

BASE_URL="http://${BACKEND_EXTERNAL_HOST}:${BACKEND_PORT}"

echo "Waiting for $BASE_URL/health ..."
for _ in $(seq 1 90); do
  if [[ "$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/health" || true)" == "200" ]]; then
    cd "$REPO_DIR"
    exec "$(python_bin)" -m pytest acceptance/ "$@"
  fi
  sleep 1
done

echo "Backend is not healthy at $BASE_URL/health — start it with run-infra.sh, migrate.sh, run-backend.sh" >&2
exit 1
