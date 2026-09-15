from statements.sql_injection_statements import INJECTED_CODE, SqlInjectionStatements

from tests.backend.abstract_backend_test import AbstractBackendTest


class TestSqlInjectionAcceptance(AbstractBackendTest):
    """Сценарий 1.3: инъекция в поля запроса не доходит до базы и не ломает запрос.

    Дано в системе есть зарегистрированный пользователь
    Когда клиент отправляет <поле> со значением, составленным как фрагмент SQL
    Тогда запрос отклоняется как некорректные данные либо обрабатывается как обычное значение
    И ни одна таблица не изменена сверх штатного поведения запроса
    И тело ответа не несёт ни текста SQL, ни имени ограничения базы данных
    """

    async def test_should_answer_a_sql_fragment_email_on_the_code_request_without_touching_a_table(
        self, sql_injection_statements: SqlInjectionStatements
    ):
        user = await sql_injection_statements.given_registered_user()
        injected_email = sql_injection_statements.sql_fragment_email()

        answer = await sql_injection_statements.request_code_with(injected_email)

        sql_injection_statements.assert_refused_as_invalid_data_or_taken_as_an_ordinary_value(answer)
        sql_injection_statements.assert_body_carries_no_sql_text_and_no_constraint_name(answer)
        sql_injection_statements.assert_body_does_not_echo(answer, injected_email)
        await sql_injection_statements.assert_registered_user_untouched(user)
        await sql_injection_statements.assert_no_account_was_created_for(injected_email)
        await sql_injection_statements.assert_queued_code_carries_the_address_verbatim(injected_email)

    async def test_should_answer_a_sql_fragment_challenge_identifier_without_touching_a_table(
        self, sql_injection_statements: SqlInjectionStatements
    ):
        user = await sql_injection_statements.given_registered_user()
        working = await sql_injection_statements.given_live_code()

        answer = await sql_injection_statements.verify_with_a_sql_fragment_challenge_id(working)

        sql_injection_statements.assert_refused_as_invalid_data_or_taken_as_an_ordinary_value(answer)
        sql_injection_statements.assert_body_carries_no_sql_text_and_no_constraint_name(answer)
        await sql_injection_statements.assert_registered_user_untouched(user)
        await sql_injection_statements.assert_live_code_still_issues_a_session(working)

    async def test_should_answer_a_sql_fragment_code_without_touching_a_table(
        self, sql_injection_statements: SqlInjectionStatements
    ):
        user = await sql_injection_statements.given_registered_user()
        working = await sql_injection_statements.given_live_code()

        answer = await sql_injection_statements.verify_with_a_sql_fragment_code(working)

        sql_injection_statements.assert_refused_as_invalid_data_or_taken_as_an_ordinary_value(answer)
        sql_injection_statements.assert_body_carries_no_sql_text_and_no_constraint_name(answer)
        sql_injection_statements.assert_body_does_not_echo(answer, INJECTED_CODE)
        await sql_injection_statements.assert_registered_user_untouched(user)
        await sql_injection_statements.assert_live_code_still_issues_a_session(working)
