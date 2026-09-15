import pytest
from clients.application.auth_client import AuthClient
from httpx import AsyncClient
from statements.auth_database import AuthDatabase
from statements.auth_statements import AuthStatements
from statements.challenge_resend_statements import ChallengeResendStatements
from statements.challenge_start_cooldown_statements import ChallengeStartCooldownStatements
from statements.concurrent_code_requests_statements import ConcurrentCodeRequestsStatements
from statements.cooldown_boundary_statements import CooldownBoundaryStatements
from statements.email_spelling_identity_statements import EmailSpellingIdentityStatements
from statements.malformed_challenge_start_statements import MalformedChallengeStartStatements
from statements.outbox_database import OutboxDatabase
from statements.second_login_statements import SecondLoginStatements


@pytest.fixture
def challenge_start_cooldown_statements(
    http_client: AsyncClient,
    auth_client: AuthClient,
    auth_statements: AuthStatements,
    outbox_database: OutboxDatabase,
) -> ChallengeStartCooldownStatements:
    return ChallengeStartCooldownStatements(http_client, auth_client, auth_statements, outbox_database)


@pytest.fixture
def malformed_challenge_start_statements(
    auth_client: AuthClient,
    auth_statements: AuthStatements,
    outbox_database: OutboxDatabase,
) -> MalformedChallengeStartStatements:
    return MalformedChallengeStartStatements(auth_client, auth_statements, outbox_database)


@pytest.fixture
def concurrent_code_requests_statements(
    http_client: AsyncClient,
    auth_statements: AuthStatements,
    challenge_start_cooldown_statements: ChallengeStartCooldownStatements,
    outbox_database: OutboxDatabase,
    auth_client: AuthClient,
) -> ConcurrentCodeRequestsStatements:

    return ConcurrentCodeRequestsStatements(
        http_client, auth_statements, challenge_start_cooldown_statements, outbox_database, auth_client
    )


@pytest.fixture
def cooldown_boundary_statements(
    auth_statements: AuthStatements,
    challenge_start_cooldown_statements: ChallengeStartCooldownStatements,
) -> CooldownBoundaryStatements:

    return CooldownBoundaryStatements(auth_statements, challenge_start_cooldown_statements)


@pytest.fixture
def challenge_resend_statements(
    auth_client: AuthClient,
    auth_statements: AuthStatements,
    outbox_database: OutboxDatabase,
) -> ChallengeResendStatements:

    return ChallengeResendStatements(auth_client, auth_statements, outbox_database)


@pytest.fixture
def email_spelling_identity_statements(
    auth_client: AuthClient,
    auth_statements: AuthStatements,
    auth_database: AuthDatabase,
    outbox_database: OutboxDatabase,
    challenge_start_cooldown_statements: ChallengeStartCooldownStatements,
) -> EmailSpellingIdentityStatements:

    return EmailSpellingIdentityStatements(
        auth_client, auth_statements, auth_database, outbox_database, challenge_start_cooldown_statements
    )


@pytest.fixture
def second_login_statements(
    auth_client: AuthClient,
    auth_statements: AuthStatements,
    auth_database: AuthDatabase,
    outbox_database: OutboxDatabase,
) -> SecondLoginStatements:
    return SecondLoginStatements(auth_client, auth_statements, auth_database, outbox_database)
