from statements.challenge_verify_statements import ChallengeVerifyStatements

from tests.backend.abstract_backend_test import AbstractBackendTest


class TestChallengeVerifyAcceptance(AbstractBackendTest):
    """Сценарий 4.1: существующий пользователь получает сессию по верному коду.

    Дано пользователь уже зарегистрирован и получил код на свой email
    Когда пользователь отправляет верный код на проверку
    Тогда ответ несёт идентификатор его существующего пользователя
    И ответ несёт идентификатор сессии, refresh-токен и access-токен
    И нового пользователя не создаётся
    """

    async def test_should_issue_a_session_for_the_existing_user_without_creating_another(
        self, challenge_verify_statements: ChallengeVerifyStatements
    ):
        registered = await challenge_verify_statements.given_registered_user_holding_a_valid_code()

        session = await challenge_verify_statements.verify_code(registered)

        challenge_verify_statements.assert_session_belongs_to_the_existing_user(session, registered)
        challenge_verify_statements.assert_session_carries_identifier_and_both_tokens(session)
        await challenge_verify_statements.assert_no_second_user_was_created(registered)
