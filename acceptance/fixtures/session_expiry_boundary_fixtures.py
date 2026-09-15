import pytest
from clients.application.auth_client import AuthClient
from statements.auth_database import AuthDatabase
from statements.session_expiry_boundary_statements import SessionExpiryBoundaryStatements
from statements.session_refresh_statements import SessionRefreshStatements


@pytest.fixture
def session_expiry_boundary_statements(
    auth_client: AuthClient,
    session_refresh_statements: SessionRefreshStatements,
    auth_database: AuthDatabase,
) -> SessionExpiryBoundaryStatements:
    return SessionExpiryBoundaryStatements(auth_client, session_refresh_statements, auth_database)
