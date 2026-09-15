import pytest
from clients.application.auth_client import AuthClient
from statements.auth_database import AuthDatabase
from statements.refresh_request_validation_statements import RefreshRequestValidationStatements
from statements.session_refresh_statements import SessionRefreshStatements


@pytest.fixture
def refresh_request_validation_statements(
    auth_client: AuthClient,
    session_refresh_statements: SessionRefreshStatements,
    auth_database: AuthDatabase,
) -> RefreshRequestValidationStatements:
    return RefreshRequestValidationStatements(auth_client, session_refresh_statements, auth_database)
