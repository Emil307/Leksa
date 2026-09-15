from statements.wrong_code_attempt_statements import WrongCodeAttemptStatements

from tests.backend.abstract_backend_test import AbstractBackendTest


class TestWrongCodeAttemptAcceptance(AbstractBackendTest):
    """Сценарий 5.1: неверный код отклоняется и тратит попытку.

    Дано пользователь получил рабочий код
    Когда пользователь отправляет неверный код на проверку
    Тогда проверка отклоняется как неудачная авторизация
    И в ответе нет ни остатка попыток, ни сессии, ни токена
    И верный код по-прежнему выдаёт сессию
    """

    async def test_should_reject_the_wrong_code_without_disclosing_attempts_and_still_accept_the_valid_one(
        self, wrong_code_attempt_statements: WrongCodeAttemptStatements
    ):
        working = await wrong_code_attempt_statements.given_user_holding_a_working_code()

        rejected = await wrong_code_attempt_statements.verify_with(
            working, wrong_code_attempt_statements.wrong_code_for(working)
        )

        wrong_code_attempt_statements.assert_rejected_as_failed_authorization(rejected)
        wrong_code_attempt_statements.assert_carries_no_attempt_remainder_no_session_and_no_token(rejected)
        await wrong_code_attempt_statements.assert_the_valid_code_still_issues_a_session(working)
