import pytest
from clients.application.auth_client import AuthClient
from statements.auth_database import AuthDatabase
from statements.auth_statements import AuthStatements
from statements.indistinguishable_refresh_refusal_statements import IndistinguishableRefreshRefusalStatements


@pytest.fixture
def indistinguishable_refresh_refusal_statements(
    auth_client: AuthClient,
    auth_statements: AuthStatements,
    auth_database: AuthDatabase,
) -> IndistinguishableRefreshRefusalStatements:
    return IndistinguishableRefreshRefusalStatements(auth_client, auth_statements, auth_database)
