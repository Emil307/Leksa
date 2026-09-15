import pytest
from clients.application.auth_client import AuthClient
from statements.auth_database import AuthDatabase
from statements.auth_statements import AuthStatements
from statements.challenge_verify_leading_zero_statements import ChallengeVerifyLeadingZeroStatements
from statements.challenge_verify_registration_statements import ChallengeVerifyRegistrationStatements
from statements.challenge_verify_statements import ChallengeVerifyStatements
from statements.challenge_verify_stored_spelling_statements import ChallengeVerifyStoredSpellingStatements
from statements.outbox_database import OutboxDatabase
from statements.token_lifetime_statements import TokenLifetimeStatements
from statements.verify_malformed_input_statements import VerifyMalformedInputStatements
from statements.wrong_code_attempt_statements import WrongCodeAttemptStatements


@pytest.fixture
def challenge_verify_statements(
    auth_client: AuthClient,
    auth_statements: AuthStatements,
    auth_database: AuthDatabase,
    outbox_database: OutboxDatabase,
) -> ChallengeVerifyStatements:
    return ChallengeVerifyStatements(auth_client, auth_statements, auth_database, outbox_database)


@pytest.fixture
def challenge_verify_registration_statements(
    auth_client: AuthClient,
    auth_statements: AuthStatements,
    auth_database: AuthDatabase,
    outbox_database: OutboxDatabase,
) -> ChallengeVerifyRegistrationStatements:
    return ChallengeVerifyRegistrationStatements(auth_client, auth_statements, auth_database, outbox_database)


@pytest.fixture
def challenge_verify_stored_spelling_statements(
    auth_client: AuthClient,
    auth_statements: AuthStatements,
    auth_database: AuthDatabase,
    outbox_database: OutboxDatabase,
) -> ChallengeVerifyStoredSpellingStatements:
    return ChallengeVerifyStoredSpellingStatements(auth_client, auth_statements, auth_database, outbox_database)


@pytest.fixture
def challenge_verify_leading_zero_statements(
    auth_client: AuthClient,
    auth_statements: AuthStatements,
    outbox_database: OutboxDatabase,
) -> ChallengeVerifyLeadingZeroStatements:
    return ChallengeVerifyLeadingZeroStatements(auth_client, auth_statements, outbox_database)


@pytest.fixture
def verify_malformed_input_statements(
    auth_client: AuthClient,
    auth_statements: AuthStatements,
    outbox_database: OutboxDatabase,
) -> VerifyMalformedInputStatements:
    return VerifyMalformedInputStatements(auth_client, auth_statements, outbox_database)


@pytest.fixture
def wrong_code_attempt_statements(
    auth_client: AuthClient,
    auth_statements: AuthStatements,
    outbox_database: OutboxDatabase,
) -> WrongCodeAttemptStatements:

    return WrongCodeAttemptStatements(auth_client, auth_statements, outbox_database)


@pytest.fixture
def token_lifetime_statements(
    auth_client: AuthClient,
    auth_statements: AuthStatements,
    auth_database: AuthDatabase,
    outbox_database: OutboxDatabase,
) -> TokenLifetimeStatements:
    return TokenLifetimeStatements(auth_client, auth_statements, auth_database, outbox_database)
