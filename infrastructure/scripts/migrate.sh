#!/usr/bin/env bash
# Applies Liquibase changesets. The application never migrates on boot.
#   migrate.sh                  -> update
#   migrate.sh --contexts=demo  -> extra arguments reach the Liquibase task
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/_env.sh"

cd "$REPO_DIR"
LIQUIBASE_URL="jdbc:postgresql://$DB_HOST:$DB_PORT/$DB_NAME" \
LIQUIBASE_USERNAME="$DB_USER" \
LIQUIBASE_PASSWORD="$DB_PASSWORD" \
  "$REPO_DIR/gradlew" --quiet :backend:adapters:storage:liquibaseUpdate "$@"
