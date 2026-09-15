from statements.pool_release_assertions import (
    assert_every_attempt_reached_its_outcome,
    assert_every_outcome_was_driven_past_pool_capacity,
    assert_no_attempt_waited_for_a_connection,
)
from statements.token_refresh_connection_release_statements import TokenRefreshConnectionReleaseStatements

from tests.backend.abstract_backend_test import AbstractBackendTest


class TestTokenRefreshConnectionReleaseAcceptance(AbstractBackendTest):
    """Инфраструктура 2.2: соединение хранилища освобождается на каждом исходе.

    Дано зафиксировано исходное число занятых соединений хранилища
    Когда успешное и ошибочное обновление токенов многократно повторяются
    Тогда после каждого вызова число занятых соединений возвращается к исходному
    И число занятых соединений не растёт от повтора к повтору
    """

    async def test_should_return_the_connection_after_every_refresh_outcome(
        self, token_refresh_connection_release_statements: TokenRefreshConnectionReleaseStatements
    ):
        outcomes = await token_refresh_connection_release_statements.given_live_session_and_every_refresh_outcome()

        attempts = await token_refresh_connection_release_statements.repeat_each_outcome_past_pool_capacity(outcomes)
        after = await token_refresh_connection_release_statements.refresh_once_more_after_every_repetition()

        assert_every_outcome_was_driven_past_pool_capacity(attempts)
        assert_every_attempt_reached_its_outcome(attempts)
        assert_no_attempt_waited_for_a_connection(attempts)
        token_refresh_connection_release_statements.assert_session_still_rotates_without_waiting(after)
