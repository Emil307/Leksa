from statements.rotation_deadlines_statements import RotationDeadlinesStatements

from tests.backend.abstract_backend_test import AbstractBackendTest


class TestRotationDeadlinesAcceptance(AbstractBackendTest):
    """API 2.2: новая пара сохраняет владельца и получает точные сроки.

    Дано существует действующая сессия с фиксированным временем ротации
    Когда клиент обновляет токены по refresh-токену этой сессии
    Тогда новый access-токен относится к прежним пользователю и сессии
    И срок access-токена равен времени ротации плюс настроенный access TTL
    И срок сессии равен времени ротации плюс настроенный refresh TTL
    И оба срока вычислены в UTC с точностью до секунды
    """

    async def test_should_keep_previous_user_and_session_in_the_new_access_token(
        self, rotation_deadlines_statements: RotationDeadlinesStatements
    ):
        previous = await rotation_deadlines_statements.given_live_session()

        deadlines = await rotation_deadlines_statements.rotate_tokens(previous)

        rotation_deadlines_statements.assert_new_access_token_belongs_to_previous_user_and_session(deadlines)

    async def test_should_set_both_deadlines_from_the_rotation_moment_and_configured_lifetimes(
        self, rotation_deadlines_statements: RotationDeadlinesStatements
    ):
        previous = await rotation_deadlines_statements.given_live_session()

        deadlines = await rotation_deadlines_statements.rotate_tokens(previous)

        rotation_deadlines_statements.assert_access_deadline_is_rotation_moment_plus_access_lifetime(deadlines)
        rotation_deadlines_statements.assert_session_deadline_is_rotation_moment_plus_refresh_lifetime(deadlines)

    async def test_should_compute_both_deadlines_in_utc_whole_seconds(
        self, rotation_deadlines_statements: RotationDeadlinesStatements
    ):
        previous = await rotation_deadlines_statements.given_live_session()

        deadlines = await rotation_deadlines_statements.rotate_tokens(previous)

        rotation_deadlines_statements.assert_both_deadlines_are_whole_utc_seconds(deadlines)
