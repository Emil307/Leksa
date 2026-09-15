import asyncpg

from statements.auth_database import connection_settings

LOCK_SESSION_ROW = "SELECT id FROM auth.t_sessions WHERE id = $1::uuid FOR UPDATE"


class SessionRowLock:
    def __init__(self) -> None:
        self._connection: asyncpg.Connection | None = None
        self._transaction: asyncpg.connection.transaction.Transaction | None = None

    async def hold(self, session_id: str) -> None:
        assert self._connection is None, "the session row lock is already held — release it before holding another"
        self._connection = await asyncpg.connect(**connection_settings())
        self._transaction = self._connection.transaction()
        await self._transaction.start()
        locked = await self._connection.fetchval(LOCK_SESSION_ROW, session_id)
        assert locked is not None, f"session {session_id!r} must exist in auth.t_sessions to lock its row, no row found"

    async def release(self) -> None:
        if self._transaction is not None:
            await self._transaction.rollback()
            self._transaction = None
        if self._connection is not None:
            await self._connection.close()
            self._connection = None
