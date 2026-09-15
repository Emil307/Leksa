from statements.session_refresh_statements import SessionRefreshStatements

from tests.backend.abstract_backend_test import AbstractBackendTest


class TestTokenRefreshAcceptance(AbstractBackendTest):
    """Сценарий 2.1: действующая сессия получает новую пару токенов.

    Дано существует действующая сессия и её access-токен ещё не истёк
    Когда клиент обновляет токены по refresh-токену этой сессии
    Тогда ответ успешен
    И ответ содержит прежний идентификатор сессии
    И ответ содержит новые refresh-токен и access-токен
    И ответ содержит только разрешённые поля сессии
    И новая строка сессии не создаётся
    """

    async def test_should_rotate_both_tokens_and_keep_the_session_identifier(
        self, session_refresh_statements: SessionRefreshStatements
    ):
        session = await session_refresh_statements.given_live_session()

        rotated = await session_refresh_statements.refresh_tokens(session)

        session_refresh_statements.assert_rotation_succeeded(rotated)
        session_refresh_statements.assert_session_identifier_is_unchanged(session, rotated)
        session_refresh_statements.assert_both_tokens_are_new(session, rotated)
        session_refresh_statements.assert_only_allowed_session_fields_are_returned(rotated)
