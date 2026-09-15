from statements.sql_metacharacter_token_statements import SqlMetacharacterTokenStatements

from tests.backend.abstract_backend_test import AbstractBackendTest


class TestSqlMetacharacterTokenAcceptance(AbstractBackendTest):
    """Сценарий 1.3: SQL-метасимволы обрабатываются как обычный неизвестный токен.

    Дано существуют сессии нескольких пользователей
    Когда клиент отправляет неизвестный refresh-токен с SQL-метасимволами
    Тогда ответ имеет единую ошибку авторизации
    И ни одна сессия не изменена
    И значение токена не появляется в журнале
    """

    async def test_should_refuse_a_tautology_token_without_touching_any_session(
        self, sql_metacharacter_token_statements: SqlMetacharacterTokenStatements
    ):
        sessions = await sql_metacharacter_token_statements.given_sessions_of_several_users()

        attempt = await sql_metacharacter_token_statements.refresh_with_tautology_token(sessions)

        sql_metacharacter_token_statements.assert_refused_with_unified_authorization_error(attempt)
        sql_metacharacter_token_statements.assert_no_session_was_changed(sessions, attempt)
        sql_metacharacter_token_statements.assert_no_session_was_opened_or_closed(sessions, attempt)

    async def test_should_refuse_a_stacked_statement_token_without_touching_any_session(
        self, sql_metacharacter_token_statements: SqlMetacharacterTokenStatements
    ):
        sessions = await sql_metacharacter_token_statements.given_sessions_of_several_users()

        attempt = await sql_metacharacter_token_statements.refresh_with_stacked_statement_token(sessions)

        sql_metacharacter_token_statements.assert_refused_with_unified_authorization_error(attempt)
        sql_metacharacter_token_statements.assert_no_session_was_changed(sessions, attempt)
        sql_metacharacter_token_statements.assert_no_session_was_opened_or_closed(sessions, attempt)
