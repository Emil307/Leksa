from collections.abc import AsyncIterator

import pytest
from clients.application.auth_client import AuthClient
from statements.auth_database import AuthDatabase
from statements.auth_statements import AuthStatements
from statements.configuration_startup_statements import ConfigurationStartupStatements
from statements.session_refresh_statements import SessionRefreshStatements
from statements.session_row_lock import SessionRowLock
from statements.storage_failure_rollback_statements import StorageFailureRollbackStatements
from statements.token_configuration_boot_statements import TokenConfigurationBootStatements
from statements.token_refresh_connection_release_statements import TokenRefreshConnectionReleaseStatements


@pytest.fixture
def configuration_startup_statements() -> ConfigurationStartupStatements:
    return ConfigurationStartupStatements()


@pytest.fixture
def token_refresh_connection_release_statements(
    auth_client: AuthClient, auth_statements: AuthStatements, session_refresh_statements: SessionRefreshStatements
) -> TokenRefreshConnectionReleaseStatements:
    return TokenRefreshConnectionReleaseStatements(auth_client, auth_statements, session_refresh_statements)


@pytest.fixture
def token_configuration_boot_statements() -> TokenConfigurationBootStatements:
    return TokenConfigurationBootStatements()


@pytest.fixture
async def session_row_lock() -> AsyncIterator[SessionRowLock]:
    lock = SessionRowLock()
    try:
        yield lock
    finally:
        await lock.release()


@pytest.fixture
def storage_failure_rollback_statements(
    auth_client: AuthClient,
    auth_statements: AuthStatements,
    session_refresh_statements: SessionRefreshStatements,
    auth_database: AuthDatabase,
    session_row_lock: SessionRowLock,
) -> StorageFailureRollbackStatements:
    return StorageFailureRollbackStatements(
        auth_client, auth_statements, session_refresh_statements, auth_database, session_row_lock
    )
