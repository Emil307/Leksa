import uuid
from datetime import datetime

import asyncpg
from clients.application.dto.profile.profile_dto import UserRecord

from statements.access_token import required_value
from statements.stored_session_row import StoredSessionRow

DB_HOST_VARIABLE = "DB_HOST"
DB_PORT_VARIABLE = "DB_PORT"
DB_NAME_VARIABLE = "DB_NAME"
DB_USER_VARIABLE = "DB_USER"
DB_PASSWORD_VARIABLE = "DB_PASSWORD"

INSERT_USER = """
INSERT INTO auth.t_users (
    id, name, surname, email, is_superuser, created_at, updated_at,
    avatar_id, birthday, gender, city, phone
) VALUES (
    $1::uuid, $2, $3, $4, $5::boolean, $6::timestamptz, $7::timestamptz,
    $8::uuid, $9::date, $10::auth.user_gender, $11, $12
)
"""

INSERT_SESSION = """
INSERT INTO auth.t_sessions (id, user_id, refresh_token, created_at, expires_at)
VALUES ($1::uuid, $2::uuid, $3, $4::timestamptz, $5::timestamptz)
"""

COUNT_USERS_WITH_EMAIL = """
SELECT count(*) FROM auth.t_users WHERE email = $1
"""

DELETE_SESSION = "DELETE FROM auth.t_sessions WHERE id = $1::uuid"

SELECT_SESSION_ROW = """
SELECT refresh_token, created_at, expires_at FROM auth.t_sessions WHERE id = $1::uuid
"""

SELECT_EMAIL_IDENTITY_USER_IDS = """
SELECT a.user_id::text FROM auth.t_auth a
JOIN auth.t_users u ON u.id = a.user_id
WHERE u.email = $1 AND a.provider = 'email'
"""

SELECT_USERS_WITH_EMAIL = """
SELECT id::text AS id, name FROM auth.t_users WHERE email = $1
"""

SELECT_USER_IDS_IGNORING_CASE_AND_SPACES = """
SELECT id::text AS id FROM auth.t_users WHERE lower(btrim(email)) = lower(btrim($1)) ORDER BY id
"""

SELECT_EMAIL_IDENTITY_USER_IDS_IGNORING_CASE_AND_SPACES = """
SELECT user_id::text AS user_id FROM auth.t_auth
WHERE provider = 'email' AND lower(btrim(provider_id)) = lower(btrim($1))
ORDER BY user_id
"""

SELECT_PROVIDER_ACCOUNTS_OF_USER = """
SELECT provider, provider_id FROM auth.t_auth WHERE user_id = $1::uuid ORDER BY provider, provider_id
"""

SELECT_SESSION_IDS_OF_USER = """
SELECT id::text AS id FROM auth.t_sessions WHERE user_id = $1::uuid ORDER BY created_at
"""

SELECT_TABLES_CARRYING_A_USER_ID = """
SELECT c.table_schema, c.table_name
FROM information_schema.columns c
JOIN information_schema.tables t
  ON t.table_schema = c.table_schema AND t.table_name = c.table_name
WHERE c.column_name = 'user_id'
  AND t.table_type = 'BASE TABLE'
  AND c.table_schema NOT IN ('pg_catalog', 'information_schema')
ORDER BY c.table_schema, c.table_name
"""

COUNT_ROWS_OF_USER = 'SELECT count(*) FROM "{schema}"."{table}" WHERE user_id = $1::uuid'


def connection_settings() -> dict[str, object]:
    return {
        "host": required_value(DB_HOST_VARIABLE),
        "port": int(required_value(DB_PORT_VARIABLE)),
        "database": required_value(DB_NAME_VARIABLE),
        "user": required_value(DB_USER_VARIABLE),
        "password": required_value(DB_PASSWORD_VARIABLE),
    }


class AuthDatabase:
    def __init__(self) -> None:
        self._connection: asyncpg.Connection | None = None

    async def open(self) -> None:
        self._connection = await asyncpg.connect(**connection_settings())

    async def close(self) -> None:
        if self._connection is not None:
            await self._connection.close()
            self._connection = None

    async def store_user(self, user: UserRecord) -> None:
        await self._require_connection().execute(
            INSERT_USER,
            user.id,
            user.name,
            user.surname,
            user.email,
            user.is_superuser,
            user.created_at,
            user.updated_at,
            user.avatar_id,
            user.birthday,
            user.gender,
            user.city,
            user.phone,
        )

    async def open_session(self, user_id: str, opened_at: datetime, expires_at: datetime) -> str:
        session_id = str(uuid.uuid4())
        await self._require_connection().execute(
            INSERT_SESSION,
            session_id,
            user_id,
            uuid.uuid4().hex,
            opened_at,
            expires_at,
        )
        return session_id

    async def stored_session_row(self, session_id: str) -> StoredSessionRow:
        row = await self._require_connection().fetchrow(SELECT_SESSION_ROW, session_id)
        assert row is not None, f"session {session_id!r} must exist in auth.t_sessions, no row found"
        return StoredSessionRow(
            refresh_token=row["refresh_token"], created_at=row["created_at"], expires_at=row["expires_at"]
        )

    async def count_users_with_email(self, email: str) -> int:
        return await self._require_connection().fetchval(COUNT_USERS_WITH_EMAIL, email)

    async def delete_session(self, session_id: str) -> str:
        return await self._require_connection().execute(DELETE_SESSION, session_id)

    async def email_identity_user_ids(self, email: str) -> list[str]:
        rows = await self._require_connection().fetch(SELECT_EMAIL_IDENTITY_USER_IDS, email)
        return [row["user_id"] for row in rows]

    async def users_with_email(self, email: str) -> list[tuple[str, str]]:
        rows = await self._require_connection().fetch(SELECT_USERS_WITH_EMAIL, email)
        return [(row["id"], row["name"]) for row in rows]

    async def user_ids_with_email_ignoring_case_and_spaces(self, email: str) -> list[str]:
        rows = await self._require_connection().fetch(SELECT_USER_IDS_IGNORING_CASE_AND_SPACES, email)
        return [row["id"] for row in rows]

    async def email_identity_user_ids_ignoring_case_and_spaces(self, email: str) -> list[str]:
        rows = await self._require_connection().fetch(SELECT_EMAIL_IDENTITY_USER_IDS_IGNORING_CASE_AND_SPACES, email)
        return [row["user_id"] for row in rows]

    async def provider_accounts_of_user(self, user_id: str) -> list[tuple[str, str]]:
        rows = await self._require_connection().fetch(SELECT_PROVIDER_ACCOUNTS_OF_USER, user_id)
        return [(row["provider"], row["provider_id"]) for row in rows]

    async def session_ids_of_user(self, user_id: str) -> list[str]:
        rows = await self._require_connection().fetch(SELECT_SESSION_IDS_OF_USER, user_id)
        return [row["id"] for row in rows]

    async def tables_holding_rows_of_user(self, user_id: str) -> list[str]:
        candidates = await self._require_connection().fetch(SELECT_TABLES_CARRYING_A_USER_ID)
        tables = [(candidate["table_schema"], candidate["table_name"]) for candidate in candidates]
        return [
            f"{schema}.{table}" for schema, table in tables if await self._holds_rows_of_user(schema, table, user_id)
        ]

    async def _holds_rows_of_user(self, schema: str, table: str, user_id: str) -> bool:
        query = COUNT_ROWS_OF_USER.format(schema=schema, table=table)
        return bool(await self._require_connection().fetchval(query, user_id))

    def _require_connection(self) -> asyncpg.Connection:
        assert self._connection is not None, "AuthDatabase must be opened before use — check the fixture"
        return self._connection
