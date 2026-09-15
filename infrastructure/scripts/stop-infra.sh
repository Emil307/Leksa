#!/usr/bin/env bash
# Stops only this repo instance's compose project — never containers started elsewhere.
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/_env.sh"

docker compose -f "$INFRA_DIR/docker-compose.yml" --env-file "$ENV_FILE" stop
echo "Stopped compose project $COMPOSE_PROJECT_NAME"
