from statements.second_login_statements import SecondLoginStatements

from tests.backend.abstract_backend_test import AbstractBackendTest


class TestSecondLoginAcceptance(AbstractBackendTest):
    """Сценарий 4.5: повторный вход по коду даёт новую сессию тому же пользователю.

    Дано пользователь уже входил по коду со своего email и держит выданную сессию
    Когда пользователь входит по коду ещё раз
    Тогда учётная запись провайдера «email» у него по-прежнему ровно одна
    И выдаётся вторая сессия с другим идентификатором и другим refresh-токеном
    И первая сессия остаётся в хранилище
    """

    async def test_should_issue_a_second_session_to_the_same_user(self, second_login_statements: SecondLoginStatements):
        first = await second_login_statements.given_a_user_who_already_logged_in_with_a_code()

        second = await second_login_statements.log_in_again(first)

        await second_login_statements.assert_the_email_account_is_still_the_only_one(first, second)
        second_login_statements.assert_a_second_session_with_another_identifier_and_another_refresh_token(first, second)
        await second_login_statements.assert_the_first_session_is_still_stored_beside_the_second(first, second)
