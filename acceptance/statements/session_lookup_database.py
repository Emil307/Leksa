from statements.auth_database import AuthDatabase

SELECT_SESSION_IDS_WITH_REFRESH_TOKEN = """
SELECT id::text AS id FROM auth.t_sessions WHERE refresh_token = $1 ORDER BY id
"""
COUNT_SESSIONS_CARRYING_FRAGMENT = """
SELECT count(*) FROM auth.t_sessions WHERE position($1 in refresh_token) > 0
"""


class SessionLookupDatabase(AuthDatabase):
    async def session_ids_with_refresh_token(self, refresh_token: str) -> list[str]:
        rows = await self._require_connection().fetch(SELECT_SESSION_IDS_WITH_REFRESH_TOKEN, refresh_token)
        return [row["id"] for row in rows]

    async def count_sessions_carrying(self, fragment: str) -> int:
        return await self._require_connection().fetchval(COUNT_SESSIONS_CARRYING_FRAGMENT, fragment)
