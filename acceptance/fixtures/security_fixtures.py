import pytest
from clients.application.auth_client import AuthClient
from clients.application.profile_client import ProfileClient
from statements.access_token_algorithm_and_claims_statements import AccessTokenAlgorithmAndClaimsStatements
from statements.auth_database import AuthDatabase
from statements.auth_statements import AuthStatements
from statements.declared_input_limits_statements import DeclaredInputLimitsStatements
from statements.foreign_challenge_id_statements import ForeignChallengeIdStatements
from statements.hostile_email_statements import HostileEmailStatements
from statements.outbox_database import OutboxDatabase
from statements.refresh_token_session_isolation_statements import RefreshTokenSessionIsolationStatements
from statements.rotation_failure_disclosure_statements import RotationFailureDisclosureStatements
from statements.rotation_request_boundary_statements import RotationRequestBoundaryStatements
from statements.server_owned_fields_statements import ServerOwnedFieldsStatements
from statements.session_lookup_database import SessionLookupDatabase
from statements.session_refresh_statements import SessionRefreshStatements
from statements.session_refusal_indistinguishability_statements import SessionRefusalIndistinguishabilityStatements
from statements.session_rotation_consistency_statements import SessionRotationConsistencyStatements
from statements.session_row_lock import SessionRowLock
from statements.sql_injection_statements import SqlInjectionStatements
from statements.sql_metacharacter_token_statements import SqlMetacharacterTokenStatements
from statements.unregistered_challenge_strategy_statements import UnregisteredChallengeStrategyStatements


@pytest.fixture
def unregistered_challenge_strategy_statements(
    auth_client: AuthClient,
    auth_statements: AuthStatements,
    outbox_database: OutboxDatabase,
) -> UnregisteredChallengeStrategyStatements:

    return UnregisteredChallengeStrategyStatements(auth_client, auth_statements, outbox_database)


@pytest.fixture
def declared_input_limits_statements(
    auth_client: AuthClient,
    auth_statements: AuthStatements,
    outbox_database: OutboxDatabase,
) -> DeclaredInputLimitsStatements:

    return DeclaredInputLimitsStatements(auth_client, auth_statements, outbox_database)


@pytest.fixture
def sql_injection_statements(
    auth_client: AuthClient,
    auth_statements: AuthStatements,
    auth_database: AuthDatabase,
    outbox_database: OutboxDatabase,
) -> SqlInjectionStatements:

    return SqlInjectionStatements(auth_client, auth_statements, auth_database, outbox_database)


@pytest.fixture
def foreign_challenge_id_statements(
    auth_client: AuthClient,
    auth_statements: AuthStatements,
    outbox_database: OutboxDatabase,
) -> ForeignChallengeIdStatements:

    return ForeignChallengeIdStatements(auth_client, auth_statements, outbox_database)


@pytest.fixture
def server_owned_fields_statements(
    auth_client: AuthClient,
    auth_statements: AuthStatements,
    auth_database: AuthDatabase,
    outbox_database: OutboxDatabase,
) -> ServerOwnedFieldsStatements:

    return ServerOwnedFieldsStatements(auth_client, auth_statements, auth_database, outbox_database)


@pytest.fixture
def hostile_email_statements(
    auth_client: AuthClient,
    auth_statements: AuthStatements,
    outbox_database: OutboxDatabase,
) -> HostileEmailStatements:

    return HostileEmailStatements(auth_client, auth_statements, outbox_database)


@pytest.fixture
def access_token_algorithm_and_claims_statements(
    auth_client: AuthClient,
    auth_statements: AuthStatements,
    session_refresh_statements: SessionRefreshStatements,
    profile_client: ProfileClient,
) -> AccessTokenAlgorithmAndClaimsStatements:
    return AccessTokenAlgorithmAndClaimsStatements(
        auth_client, auth_statements, session_refresh_statements, profile_client
    )


@pytest.fixture
def refresh_token_session_isolation_statements(
    auth_client: AuthClient,
    session_rotation_consistency_statements: SessionRotationConsistencyStatements,
    session_refresh_statements: SessionRefreshStatements,
    auth_database: AuthDatabase,
) -> RefreshTokenSessionIsolationStatements:
    return RefreshTokenSessionIsolationStatements(
        auth_client, session_rotation_consistency_statements, session_refresh_statements, auth_database
    )


@pytest.fixture
def sql_metacharacter_token_statements(
    auth_client: AuthClient,
    auth_statements: AuthStatements,
    auth_database: AuthDatabase,
) -> SqlMetacharacterTokenStatements:

    return SqlMetacharacterTokenStatements(auth_client, auth_statements, auth_database)


@pytest.fixture
def session_refusal_indistinguishability_statements(
    auth_client: AuthClient,
    auth_statements: AuthStatements,
    auth_database: AuthDatabase,
) -> SessionRefusalIndistinguishabilityStatements:

    return SessionRefusalIndistinguishabilityStatements(auth_client, auth_statements, auth_database)


@pytest.fixture
def rotation_request_boundary_statements(
    auth_client: AuthClient, auth_statements: AuthStatements, session_lookup_database: SessionLookupDatabase
) -> RotationRequestBoundaryStatements:
    return RotationRequestBoundaryStatements(auth_client, auth_statements, session_lookup_database)


@pytest.fixture
def rotation_failure_disclosure_statements(
    auth_client: AuthClient, auth_statements: AuthStatements, session_row_lock: SessionRowLock
) -> RotationFailureDisclosureStatements:
    return RotationFailureDisclosureStatements(auth_client, auth_statements, session_row_lock)
