from collections.abc import AsyncIterator

import pytest
from clients.application.application_client import resolve_base_url
from clients.application.auth_client import AuthClient
from clients.application.health_client import HealthClient
from clients.application.profile_client import ProfileClient
from httpx import AsyncClient
from statements.auth_database import AuthDatabase
from statements.auth_statements import AuthStatements
from statements.health_statements import HealthStatements
from statements.outbox_database import OutboxDatabase
from statements.session_refresh_statements import SessionRefreshStatements
from statements.session_rotation_consistency_statements import SessionRotationConsistencyStatements
from statements.wire_contract import REQUEST_TIMEOUT_SECONDS

pytest_plugins = [
    "fixtures.challenge_start_fixtures",
    "fixtures.challenge_verify_fixtures",
    "fixtures.challenge_lifecycle_fixtures",
    "fixtures.security_fixtures",
    "fixtures.infrastructure_fixtures",
    "fixtures.conditional_write_single_winner_fixtures",
    "fixtures.session_expiry_boundary_fixtures",
    "fixtures.session_refusal_fixtures",
    "fixtures.session_refresh_validation_fixtures",
    "fixtures.session_rotation_fixtures",
    "fixtures.rotation_deadlines_fixtures",
    "fixtures.neighbor_session_isolation_fixtures",
    "fixtures.ttl_fraction_fixtures",
    "fixtures.refresh_request_validation_fixtures",
]


@pytest.fixture
async def http_client() -> AsyncIterator[AsyncClient]:
    async with AsyncClient(base_url=resolve_base_url(), timeout=REQUEST_TIMEOUT_SECONDS) as client:
        yield client


@pytest.fixture
async def auth_database() -> AsyncIterator[AuthDatabase]:
    database = AuthDatabase()
    await database.open()
    try:
        yield database
    finally:
        await database.close()


@pytest.fixture
def profile_client(http_client: AsyncClient) -> ProfileClient:
    return ProfileClient(http_client)


@pytest.fixture
def health_client(http_client: AsyncClient) -> HealthClient:
    return HealthClient(http_client)


@pytest.fixture
def health_statements(health_client: HealthClient) -> HealthStatements:
    return HealthStatements(health_client)


@pytest.fixture
def auth_client(http_client: AsyncClient) -> AuthClient:
    return AuthClient(http_client)


@pytest.fixture
def auth_statements(auth_client: AuthClient, outbox_database: OutboxDatabase) -> AuthStatements:
    return AuthStatements(auth_client, outbox_database)


@pytest.fixture
def session_refresh_statements(auth_client: AuthClient, auth_statements: AuthStatements) -> SessionRefreshStatements:
    return SessionRefreshStatements(auth_client, auth_statements)


@pytest.fixture
def session_rotation_consistency_statements(
    auth_client: AuthClient,
    auth_statements: AuthStatements,
    session_refresh_statements: SessionRefreshStatements,
    profile_client: ProfileClient,
    auth_database: AuthDatabase,
) -> SessionRotationConsistencyStatements:
    return SessionRotationConsistencyStatements(
        auth_client, auth_statements, session_refresh_statements, profile_client, auth_database
    )


@pytest.fixture
async def outbox_database() -> AsyncIterator[OutboxDatabase]:
    database = OutboxDatabase()
    await database.open()
    try:
        yield database
    finally:
        await database.close()
