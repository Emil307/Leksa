#!/usr/bin/env bash
# Sourced by every API script here: resolves the API root and exports infrastructure/.env.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INFRA_DIR="$(dirname "$SCRIPT_DIR")"
REPO_DIR="$(dirname "$INFRA_DIR")"
ENV_FILE="$INFRA_DIR/.env"

if [[ ! -f "$ENV_FILE" ]]; then
  "$SCRIPT_DIR/setup-ports.sh"
fi

set -a
# shellcheck disable=SC1090
source "$ENV_FILE"
set +a

export REPO_DIR INFRA_DIR ENV_FILE

python_bin() {
  if [[ -x "$REPO_DIR/.venv/bin/python" ]]; then
    echo "$REPO_DIR/.venv/bin/python"
  else
    echo "python3"
  fi
}

java_bin() {
  if [[ -n "${JAVA_HOME:-}" && -x "$JAVA_HOME/bin/java" ]]; then
    echo "$JAVA_HOME/bin/java"
  else
    echo "java"
  fi
}

app_jar() {
  local jar
  jar="$(ls "$REPO_DIR"/backend/application/build/libs/*.jar 2>/dev/null | grep -v -- '-plain\.jar$' | head -1 || true)"
  if [[ -z "$jar" ]]; then
    echo "No application jar — build it with ./gradlew :backend:application:bootJar" >&2
    return 1
  fi
  echo "$jar"
}
