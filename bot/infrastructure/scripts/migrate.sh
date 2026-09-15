#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/_env.sh"

if [[ $# -eq 0 ]]; then
  set -- upgrade head
fi

compose run --rm --no-deps bot alembic -c alembic.ini "$@"
