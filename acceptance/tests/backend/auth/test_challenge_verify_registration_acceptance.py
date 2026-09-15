from statements.challenge_verify_registration_statements import ChallengeVerifyRegistrationStatements

from tests.backend.abstract_backend_test import AbstractBackendTest


class TestChallengeVerifyRegistrationAcceptance(AbstractBackendTest):
    """Сценарий 4.2: неизвестный email регистрируется при верном коде и получает сессию.

    Дано email не принадлежит ни одному пользователю
    И клиент запросил код на этот email
    Когда пользователь отправляет верный код на проверку
    Тогда создаётся ровно один пользователь с пустым именем
    И создаётся ровно одна учётная запись провайдера «email» для нормализованного адреса
    И создаётся ровно одна сессия
    И ни строки профиля, ни строки онбординга не появляется
    """

    async def test_should_register_the_unknown_email_and_issue_its_first_session(
        self, challenge_verify_registration_statements: ChallengeVerifyRegistrationStatements
    ):
        unknown = await challenge_verify_registration_statements.given_a_code_requested_for_an_email_no_user_owns()

        session = await challenge_verify_registration_statements.verify_code(unknown)

        await challenge_verify_registration_statements.assert_exactly_one_user_with_an_empty_name(session, unknown)
        await challenge_verify_registration_statements.assert_exactly_one_email_account_for_the_normalized_address(
            session, unknown
        )
        await challenge_verify_registration_statements.assert_exactly_one_session_carrying_the_answered_identifier(
            session
        )
        await challenge_verify_registration_statements.assert_no_profile_and_no_onboarding_row_appears(session)
