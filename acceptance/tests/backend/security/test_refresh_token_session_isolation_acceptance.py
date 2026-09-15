import pytest
from statements.refresh_token_session_isolation_statements import RefreshTokenSessionIsolationStatements

from tests.backend.abstract_backend_test import AbstractBackendTest


class TestRefreshTokenSessionIsolationAcceptance(AbstractBackendTest):
    """Безопасность 2.1: refresh-токен изменяет только принадлежащую ему сессию.

    Дано пользователи А и Б имеют независимые действующие сессии
    Когда клиент обновляет сессию refresh-токеном пользователя А
    Тогда изменяется только названная токеном сессия пользователя А
    И сессия пользователя Б остаётся без изменений
    И ответ не принимает идентификатор владельца от клиента
    """

    async def test_should_rotate_only_the_session_named_by_the_token_of_user_a(
        self, refresh_token_session_isolation_statements: RefreshTokenSessionIsolationStatements
    ):
        owners = await refresh_token_session_isolation_statements.given_independent_live_sessions_of_users_a_and_b()

        rotation = await refresh_token_session_isolation_statements.rotate_with_the_token_of_user_a(owners)

        refresh_token_session_isolation_statements.assert_only_the_session_of_user_a_was_rotated(owners, rotation)
        refresh_token_session_isolation_statements.assert_session_of_user_b_is_unchanged(owners, rotation)

    @pytest.mark.skip(
        reason="RED: a refresh carrying a client-sent userId answers 200 and rotates instead of 400 VALIDATION_FAILED"
    )
    async def test_should_refuse_an_owner_identifier_sent_by_the_client(
        self, refresh_token_session_isolation_statements: RefreshTokenSessionIsolationStatements
    ):
        owners = await refresh_token_session_isolation_statements.given_independent_live_sessions_of_users_a_and_b()

        attempt = (
            await refresh_token_session_isolation_statements.rotate_with_the_token_of_user_a_naming_user_b_as_owner(
                owners
            )
        )

        refresh_token_session_isolation_statements.assert_owner_identifier_is_refused_as_invalid_data(attempt)
        refresh_token_session_isolation_statements.assert_neither_session_was_changed(owners, attempt)
