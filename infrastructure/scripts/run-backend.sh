#!/usr/bin/env bash
# Starts the Spring Boot application in the foreground on the port from infrastructure/.env.
# Run it as a background command from the caller — never hardcode the port here.
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/_env.sh"

cd "$REPO_DIR"
"$REPO_DIR/gradlew" --quiet :backend:application:bootJar
jar="$(app_jar)"

echo "Starting backend on http://localhost:$BACKEND_PORT (health: /health)"
exec "$(java_bin)" -jar "$jar" "$@"
