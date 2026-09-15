from statements.challenge_verify_stored_spelling_statements import ChallengeVerifyStoredSpellingStatements

from tests.backend.abstract_backend_test import AbstractBackendTest


class TestChallengeVerifyStoredSpellingAcceptance(AbstractBackendTest):
    """Сценарий 4.6: пользователь, чей email записан в базе в другом написании, не получает второго аккаунта.

    Дано пользователь уже заведён в базе с адресом <написание в базе>
    И клиент запросил код на тот же адрес в нижнем регистре
    Когда пользователь отправляет верный код на проверку
    Тогда ответ несёт идентификатор того самого заведённого пользователя
    И второго пользователя с этим адресом не появляется
    И учётная запись провайдера «email» указывает на заведённого пользователя

    Написание в базе: разный регистр (`Ivan@Uwords.App`); с окружающими пробелами (` ivan@uwords.app `).
    """

    async def test_should_answer_with_the_user_stored_in_another_case(
        self, challenge_verify_stored_spelling_statements: ChallengeVerifyStoredSpellingStatements
    ):
        seeded = await challenge_verify_stored_spelling_statements.given_user_stored_in_another_case_holding_a_code()

        session = await challenge_verify_stored_spelling_statements.verify_code(seeded)

        challenge_verify_stored_spelling_statements.assert_session_belongs_to_the_stored_user(session, seeded)
        await challenge_verify_stored_spelling_statements.assert_the_session_is_the_stored_users_only_one(
            session, seeded
        )
        await challenge_verify_stored_spelling_statements.assert_no_second_user_owns_the_address_in_any_spelling(seeded)
        await challenge_verify_stored_spelling_statements.assert_email_account_points_at_the_stored_user(seeded)
        await challenge_verify_stored_spelling_statements.assert_no_second_identity_holds_the_address_in_any_spelling(
            seeded
        )

    async def test_should_answer_with_the_user_stored_with_surrounding_spaces(
        self, challenge_verify_stored_spelling_statements: ChallengeVerifyStoredSpellingStatements
    ):
        seeded = (
            await challenge_verify_stored_spelling_statements.given_user_stored_with_surrounding_spaces_holding_a_code()
        )

        session = await challenge_verify_stored_spelling_statements.verify_code(seeded)

        challenge_verify_stored_spelling_statements.assert_session_belongs_to_the_stored_user(session, seeded)
        await challenge_verify_stored_spelling_statements.assert_the_session_is_the_stored_users_only_one(
            session, seeded
        )
        await challenge_verify_stored_spelling_statements.assert_no_second_user_owns_the_address_in_any_spelling(seeded)
        await challenge_verify_stored_spelling_statements.assert_email_account_points_at_the_stored_user(seeded)
        await challenge_verify_stored_spelling_statements.assert_no_second_identity_holds_the_address_in_any_spelling(
            seeded
        )
