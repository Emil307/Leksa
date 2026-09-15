import pytest
from clients.application.auth_client import AuthClient
from statements.auth_database import AuthDatabase
from statements.auth_statements import AuthStatements
from statements.session_refresh_statements import SessionRefreshStatements
from statements.ttl_fraction_statements import TtlFractionStatements


@pytest.fixture
def ttl_fraction_statements(
    auth_client: AuthClient,
    auth_statements: AuthStatements,
    session_refresh_statements: SessionRefreshStatements,
    auth_database: AuthDatabase,
) -> TtlFractionStatements:
    return TtlFractionStatements(auth_client, auth_statements, session_refresh_statements, auth_database)
