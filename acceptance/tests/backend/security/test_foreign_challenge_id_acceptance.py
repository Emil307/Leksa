from statements.foreign_challenge_id_statements import ForeignChallengeIdStatements

from tests.backend.abstract_backend_test import AbstractBackendTest


class TestForeignChallengeIdAcceptance(AbstractBackendTest):
    """Сценарий 3.1: чужой идентификатор challenge не даёт ни сессии, ни сведений о существовании.

    Дано два разных пользователя получили каждый свой код
    Когда первый пользователь предъявляет идентификатор challenge второго со своим кодом
    Тогда проверка отклоняется как неудачная авторизация
    И сессия второму пользователю не выдаётся
    И ответ не отличается от ответа на неверный код по собственному живому challenge
    И попытки у challenge первого пользователя не тратятся
    И верный код второго пользователя по-прежнему выдаёт сессию
    """

    async def test_should_refuse_a_foreign_challenge_id_exactly_as_a_wrong_code_without_spending_own_attempts(
        self, foreign_challenge_id_statements: ForeignChallengeIdStatements
    ):
        users = await foreign_challenge_id_statements.given_two_users_each_holding_their_own_code()
        before = await foreign_challenge_id_statements.attempts_of_the_first_challenge(users)

        foreign = await foreign_challenge_id_statements.the_first_user_presents_the_challenge_id_of_the_second(users)

        foreign_challenge_id_statements.assert_rejected_as_failed_authorization(foreign)
        foreign_challenge_id_statements.assert_carries_no_session_and_no_token(foreign)
        await foreign_challenge_id_statements.assert_the_attempts_of_the_first_challenge_are_untouched(users, before)

        own = await foreign_challenge_id_statements.the_first_user_presents_a_wrong_code_on_their_own_challenge(users)

        foreign_challenge_id_statements.assert_rejected_as_failed_authorization(own)
        await foreign_challenge_id_statements.assert_a_wrong_code_on_the_own_challenge_does_spend_one(users, before)
        foreign_challenge_id_statements.assert_indistinguishable_from_a_wrong_code_on_the_own_challenge(foreign, own)
        await foreign_challenge_id_statements.assert_the_second_user_code_still_issues_a_session(users)
