import pytest
from clients.application.profile_client import ProfileClient
from httpx import AsyncClient
from statements.auth_database import AuthDatabase
from statements.connection_release_statements import ConnectionReleaseStatements

from tests.backend.abstract_backend_test import AbstractBackendTest


@pytest.fixture
def connection_release_statements(http_client: AsyncClient, auth_database: AuthDatabase) -> ConnectionReleaseStatements:
    return ConnectionReleaseStatements(ProfileClient(http_client), auth_database)


class TestConnectionReleaseAcceptance(AbstractBackendTest):
    """Сценарий 2.1: проверка сессии освобождает соединение на каждом исходе.

    Дано пул соединений PostgreSQL находится на исходном уровне
    Когда много запросов профиля завершаются успехом и отказом сессии
    Тогда после каждого исхода число занятых соединений возвращается к исходному уровню
    И последующие запросы продолжают получать соединение
    """

    async def test_should_return_each_connection_to_the_pool_after_every_outcome(
        self, connection_release_statements: ConnectionReleaseStatements
    ):
        outcomes = await connection_release_statements.given_pool_at_rest_and_every_reachable_outcome()

        attempts = await connection_release_statements.drive_each_outcome_past_pool_capacity(outcomes)

        connection_release_statements.assert_every_outcome_was_driven_past_pool_capacity(attempts)
        connection_release_statements.assert_every_attempt_reached_its_outcome(attempts)
        connection_release_statements.assert_no_attempt_waited_for_a_connection(attempts)
        await connection_release_statements.assert_later_requests_still_obtain_a_connection()
