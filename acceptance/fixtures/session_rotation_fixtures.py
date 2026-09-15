import pytest
from clients.application.auth_client import AuthClient
from clients.application.profile_client import ProfileClient
from statements.auth_database import AuthDatabase
from statements.concurrent_rotation_statements import ConcurrentRotationStatements
from statements.lost_rotation_response_statements import LostRotationResponseStatements
from statements.session_refresh_statements import SessionRefreshStatements
from statements.session_rotation_consistency_statements import SessionRotationConsistencyStatements


@pytest.fixture
def concurrent_rotation_statements(
    auth_client: AuthClient,
    session_refresh_statements: SessionRefreshStatements,
    session_rotation_consistency_statements: SessionRotationConsistencyStatements,
    profile_client: ProfileClient,
    auth_database: AuthDatabase,
) -> ConcurrentRotationStatements:
    return ConcurrentRotationStatements(
        auth_client, session_refresh_statements, session_rotation_consistency_statements, profile_client, auth_database
    )


@pytest.fixture
def lost_rotation_response_statements(
    auth_client: AuthClient,
    session_refresh_statements: SessionRefreshStatements,
    session_rotation_consistency_statements: SessionRotationConsistencyStatements,
    profile_client: ProfileClient,
    auth_database: AuthDatabase,
) -> LostRotationResponseStatements:
    return LostRotationResponseStatements(
        auth_client, session_refresh_statements, session_rotation_consistency_statements, profile_client, auth_database
    )
