import asyncpg

from statements.auth_database import connection_settings

QUEUED_EMAIL_CODE = """
SELECT data->'variables'->>'code'
FROM notifications.t_outbox
WHERE type = 'EMAIL' AND data->>'to' = $1
ORDER BY created_at DESC
LIMIT 1
"""


class OutboxDatabase:
    def __init__(self) -> None:
        self._connection: asyncpg.Connection | None = None

    async def open(self) -> None:
        self._connection = await asyncpg.connect(**connection_settings())

    async def close(self) -> None:
        if self._connection is not None:
            await self._connection.close()
            self._connection = None

    async def queued_code_for(self, email: str) -> str | None:
        return await self._require_connection().fetchval(QUEUED_EMAIL_CODE, email)

    def _require_connection(self) -> asyncpg.Connection:
        assert self._connection is not None, "OutboxDatabase must be opened before use — check the fixture"
        return self._connection
