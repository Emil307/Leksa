import pytest
from clients.application.profile_client import ProfileClient
from statements.auth_database import AuthDatabase
from statements.profile_statements import ProfileStatements


@pytest.fixture
def profile_statements(profile_client: ProfileClient, auth_database: AuthDatabase) -> ProfileStatements:
    return ProfileStatements(profile_client, auth_database)
