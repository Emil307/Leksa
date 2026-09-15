import pytest
from statements.concurrent_verify_registration_statements import ConcurrentVerifyRegistrationStatements

from tests.backend.abstract_backend_test import AbstractBackendTest

RED_REASON = (
    "RED: both concurrent verifications must answer 200 with a session, got [200, 500] — "
    "auto-registration reads and inserts the user without guarding the unique key, so the race "
    "loser surfaces a uniqueness violation as Internal Server Error instead of receiving a session"
)


@pytest.mark.skip(reason=RED_REASON)
class TestConcurrentVerifyRegistrationAcceptance(AbstractBackendTest):
    """Сценарий 7.3: две одновременные проверки для нового email создают одного пользователя.

    Дано email не принадлежит ни одному пользователю
    И пользователь получил рабочий код
    Когда две проверки с одной и той же парой «идентификатор challenge и код» доведены до управляемой
    точки синхронизации внутри транзакции авторегистрации и отпущены вместе
    Тогда создаётся ровно один пользователь
    И создаётся ровно одна учётная запись провайдера «email»
    И проигравший гонку запрос получает сессию, а не ошибку нарушения уникальности
    """

    async def test_should_create_one_user_when_two_verifications_race_for_the_same_new_email(
        self, concurrent_verify_registration_statements: ConcurrentVerifyRegistrationStatements
    ):
        unclaimed = await concurrent_verify_registration_statements.given_a_working_code_for_an_email_no_user_owns()

        outcome = await concurrent_verify_registration_statements.release_two_verifications_together(unclaimed)

        await concurrent_verify_registration_statements.assert_exactly_one_user_owns_the_email(unclaimed)
        await concurrent_verify_registration_statements.assert_exactly_one_email_account_for_that_user(unclaimed)
        concurrent_verify_registration_statements.assert_the_race_loser_got_a_session_not_a_uniqueness_violation(
            outcome
        )
        concurrent_verify_registration_statements.assert_both_sessions_belong_to_the_same_user(outcome)
