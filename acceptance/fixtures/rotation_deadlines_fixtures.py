import pytest
from clients.application.auth_client import AuthClient
from statements.auth_database import AuthDatabase
from statements.auth_statements import AuthStatements
from statements.rotation_deadlines_statements import RotationDeadlinesStatements
from statements.session_refresh_statements import SessionRefreshStatements


@pytest.fixture
def rotation_deadlines_statements(
    auth_client: AuthClient,
    auth_statements: AuthStatements,
    session_refresh_statements: SessionRefreshStatements,
    auth_database: AuthDatabase,
) -> RotationDeadlinesStatements:
    return RotationDeadlinesStatements(auth_client, auth_statements, session_refresh_statements, auth_database)
