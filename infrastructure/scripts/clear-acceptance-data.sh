#!/usr/bin/env bash
# Removes the rows the black-box acceptance suite leaves behind in this repo's own
# database: identities on the acceptance email domain and their queued mail.
# Every other row is left untouched — this never truncates a table.
#   clear-acceptance-data.sh            -> report what would be removed, change nothing
#   clear-acceptance-data.sh --apply    -> remove them
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/_env.sh"

EMAIL_DOMAIN="uwords-acceptance.local"
CONTAINER="postgres-container-${REPO_INDEX}"

psql_do() {
  docker exec -i "$CONTAINER" psql -v ON_ERROR_STOP=1 -U "$DB_USER" -d "$DB_NAME" "$@"
}

REPORT_SQL="
SELECT 'auth.t_users' AS relation, count(*) AS rows FROM auth.t_users
WHERE btrim(email) ILIKE '%@${EMAIL_DOMAIN}'
UNION ALL
SELECT 'auth.t_sessions', count(*) FROM auth.t_sessions s
WHERE s.user_id IN (SELECT id FROM auth.t_users WHERE btrim(email) ILIKE '%@${EMAIL_DOMAIN}')
UNION ALL
SELECT 'notifications.t_outbox', count(*) FROM notifications.t_outbox
WHERE data->>'to' ILIKE '%@${EMAIL_DOMAIN}';
"

DELETE_SQL="
BEGIN;
DELETE FROM auth.t_sessions
WHERE user_id IN (SELECT id FROM auth.t_users WHERE btrim(email) ILIKE '%@${EMAIL_DOMAIN}');
DELETE FROM auth.t_auth
WHERE user_id IN (SELECT id FROM auth.t_users WHERE btrim(email) ILIKE '%@${EMAIL_DOMAIN}');
DELETE FROM auth.t_users WHERE btrim(email) ILIKE '%@${EMAIL_DOMAIN}';
DELETE FROM notifications.t_outbox WHERE data->>'to' ILIKE '%@${EMAIL_DOMAIN}';
COMMIT;
"

echo "Acceptance rows in ${CONTAINER} (${DB_NAME}), domain @${EMAIL_DOMAIN}:"
psql_do -c "$REPORT_SQL"

if [[ "${1:-}" != "--apply" ]]; then
  echo "Dry run — nothing removed. Re-run with --apply to remove these rows."
  exit 0
fi

psql_do <<<"$DELETE_SQL"
echo "Removed. Remaining:"
psql_do -c "$REPORT_SQL"
