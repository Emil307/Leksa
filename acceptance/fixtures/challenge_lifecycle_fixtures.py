import pytest
from clients.application.auth_client import AuthClient
from httpx import AsyncClient
from statements.auth_database import AuthDatabase
from statements.auth_statements import AuthStatements
from statements.challenge_verify_statements import ChallengeVerifyStatements
from statements.concurrent_verify_registration_statements import ConcurrentVerifyRegistrationStatements
from statements.concurrent_verify_statements import ConcurrentVerifyStatements
from statements.expired_and_unknown_challenge_statements import ExpiredAndUnknownChallengeStatements
from statements.last_attempt_success_statements import LastAttemptSuccessStatements
from statements.outbox_database import OutboxDatabase
from statements.same_session_replay_statements import SameSessionReplayStatements
from statements.terminal_challenge_statements import TerminalChallengeStatements


@pytest.fixture
def expired_and_unknown_challenge_statements(
    auth_client: AuthClient,
    auth_statements: AuthStatements,
    outbox_database: OutboxDatabase,
) -> ExpiredAndUnknownChallengeStatements:
    return ExpiredAndUnknownChallengeStatements(auth_client, auth_statements, outbox_database)


@pytest.fixture
def terminal_challenge_statements(
    auth_client: AuthClient,
    auth_statements: AuthStatements,
    auth_database: AuthDatabase,
    outbox_database: OutboxDatabase,
) -> TerminalChallengeStatements:

    return TerminalChallengeStatements(auth_client, auth_statements, auth_database, outbox_database)


@pytest.fixture
def last_attempt_success_statements(
    http_client: AsyncClient,
    auth_client: AuthClient,
    auth_statements: AuthStatements,
    outbox_database: OutboxDatabase,
) -> LastAttemptSuccessStatements:

    return LastAttemptSuccessStatements(http_client, auth_client, auth_statements, outbox_database)


@pytest.fixture
def same_session_replay_statements(
    auth_client: AuthClient,
    auth_statements: AuthStatements,
    auth_database: AuthDatabase,
    outbox_database: OutboxDatabase,
) -> SameSessionReplayStatements:

    return SameSessionReplayStatements(auth_client, auth_statements, auth_database, outbox_database)


@pytest.fixture
def concurrent_verify_statements(
    auth_client: AuthClient,
    challenge_verify_statements: ChallengeVerifyStatements,
    auth_database: AuthDatabase,
) -> ConcurrentVerifyStatements:

    return ConcurrentVerifyStatements(auth_client, challenge_verify_statements, auth_database)


@pytest.fixture
def concurrent_verify_registration_statements(
    auth_client: AuthClient,
    auth_statements: AuthStatements,
    auth_database: AuthDatabase,
    outbox_database: OutboxDatabase,
) -> ConcurrentVerifyRegistrationStatements:

    return ConcurrentVerifyRegistrationStatements(auth_client, auth_statements, auth_database, outbox_database)
