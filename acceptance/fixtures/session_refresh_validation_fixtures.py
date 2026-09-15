from collections.abc import AsyncIterator

import pytest
from clients.application.auth_client import AuthClient
from statements.auth_statements import AuthStatements
from statements.max_length_refresh_token_statements import MaxLengthRefreshTokenStatements
from statements.session_lookup_database import SessionLookupDatabase


@pytest.fixture
async def session_lookup_database() -> AsyncIterator[SessionLookupDatabase]:
    database = SessionLookupDatabase()
    await database.open()
    try:
        yield database
    finally:
        await database.close()


@pytest.fixture
def max_length_refresh_token_statements(
    auth_client: AuthClient, auth_statements: AuthStatements, session_lookup_database: SessionLookupDatabase
) -> MaxLengthRefreshTokenStatements:
    return MaxLengthRefreshTokenStatements(auth_client, auth_statements, session_lookup_database)
