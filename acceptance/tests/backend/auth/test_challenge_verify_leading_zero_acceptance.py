from statements.challenge_verify_leading_zero_statements import ChallengeVerifyLeadingZeroStatements

from tests.backend.abstract_backend_test import AbstractBackendTest


class TestChallengeVerifyLeadingZeroAcceptance(AbstractBackendTest):
    """Сценарий 4.3: код с ведущим нулём проходит весь путь.

    Дано сгенерированный код начинается с нуля
    Когда пользователь берёт код из заявки и отправляет его на проверку без изменений
    Тогда выдаётся сессия
    И ведущий ноль не потерян ни в заявке, ни при проверке
    """

    async def test_should_issue_a_session_for_a_code_whose_leading_zero_survived_the_whole_path(
        self, challenge_verify_leading_zero_statements: ChallengeVerifyLeadingZeroStatements
    ):
        statements = challenge_verify_leading_zero_statements
        requested = await statements.given_a_generated_code_starting_with_zero()

        shortened = await statements.verify_code_without_its_leading_zero(requested)
        session = await statements.verify_code_unchanged(requested)

        statements.assert_the_shortened_code_was_rejected(shortened, requested)
        statements.assert_session_was_issued(session)
        await statements.assert_the_queued_code_kept_its_leading_zero(requested)
