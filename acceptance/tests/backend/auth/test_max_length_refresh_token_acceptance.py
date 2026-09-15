from statements.max_length_refresh_token_statements import MaxLengthRefreshTokenStatements

from tests.backend.abstract_backend_test import AbstractBackendTest


class TestMaxLengthRefreshTokenAcceptance(AbstractBackendTest):
    """Сценарий 1.3: ASCII-токен предельной длины проходит валидацию.

    Дано в хранилище нет сессии для ASCII-токена длиной 512 байт
    Когда клиент отправляет обновление с этим refresh-токеном
    Тогда ответ имеет единую ошибку авторизации
    И ответ не имеет ошибки валидации
    И ни одна сессия не изменена
    """

    async def test_should_refuse_the_unknown_max_length_token_as_unauthorized_without_touching_sessions(
        self, max_length_refresh_token_statements: MaxLengthRefreshTokenStatements
    ):
        unknown = await max_length_refresh_token_statements.given_no_session_for_a_max_length_ascii_token()

        outcome = await max_length_refresh_token_statements.refresh_with_the_token(unknown)

        max_length_refresh_token_statements.assert_unified_authorization_refusal(outcome)
        max_length_refresh_token_statements.assert_no_validation_error(outcome)
        max_length_refresh_token_statements.assert_no_session_was_changed(unknown, outcome)
