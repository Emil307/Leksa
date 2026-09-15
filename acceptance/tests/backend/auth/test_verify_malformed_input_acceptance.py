from statements.verify_malformed_input_statements import VerifyMalformedInputStatements

from tests.backend.abstract_backend_test import AbstractBackendTest


class TestVerifyMalformedInputAcceptance(AbstractBackendTest):
    """Сценарий 3.1: некорректный ввод на проверке кода отклоняется.

    Дано пользователь получил рабочий код
    Когда клиент отправляет на проверку <поле> со значением <значение>
    Тогда запрос отклоняется как некорректные данные
    И попытка у живого challenge не тратится
    И значение не приводится к другому типу молча
    И верный код по-прежнему выдаёт сессию
    """

    async def test_should_reject_every_malformed_challenge_identifier_and_keep_the_live_challenge_usable(
        self, verify_malformed_input_statements: VerifyMalformedInputStatements
    ):
        working = await verify_malformed_input_statements.given_user_holding_a_working_code()

        await verify_malformed_input_statements.send_each_and_assert_rejected_as_invalid_input(
            verify_malformed_input_statements.malformed_challenge_identifiers(working)
        )

        await verify_malformed_input_statements.assert_attempts_untouched_and_valid_code_still_issues_a_session(working)

    async def test_should_reject_every_malformed_code_and_keep_the_live_challenge_usable(
        self, verify_malformed_input_statements: VerifyMalformedInputStatements
    ):
        working = await verify_malformed_input_statements.given_user_holding_a_working_code()

        await verify_malformed_input_statements.send_each_and_assert_rejected_as_invalid_input(
            verify_malformed_input_statements.malformed_codes(working)
        )

        await verify_malformed_input_statements.assert_attempts_untouched_and_valid_code_still_issues_a_session(working)
