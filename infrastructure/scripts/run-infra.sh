#!/usr/bin/env bash
# Starts PostgreSQL, Redis and MailHog for THIS repo instance only.
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/_env.sh"

docker compose -f "$INFRA_DIR/docker-compose.yml" --env-file "$ENV_FILE" up -d

wait_for() {
  local label="$1"
  shift
  for _ in $(seq 1 40); do
    if "$@" >/dev/null 2>&1; then
      return 0
    fi
    sleep 1
  done
  echo "$label did not become ready in time" >&2
  return 1
}

echo "Waiting for PostgreSQL on port $DB_PORT ..."
wait_for PostgreSQL docker exec "postgres-container-$REPO_INDEX" \
  pg_isready -U "$DB_USER" -d "$DB_NAME"

echo "Waiting for Redis on port $REDIS_PORT ..."
wait_for Redis docker exec "redis-container-$REPO_INDEX" \
  sh -c 'redis-cli --no-auth-warning -a "$REDIS_PASSWORD" ping | grep -q PONG'

echo "PostgreSQL ready (port $DB_PORT), Redis ready (port $REDIS_PORT), MailHog UI on http://localhost:$MAILHOG_HTTP_PORT"
