import pytest
from statements.last_attempt_success_statements import LastAttemptSuccessStatements

from tests.backend.abstract_backend_test import AbstractBackendTest

RED_REASON = (
    "RED: the correct code presented on attempt 5 of 5 — the last allowed one — must be accepted "
    "with 200, got 500 — claim_attempt reports the final attempt as exhausted and drops the record "
    "before the presented code is compared, so POST /api/v1/auth/challenge/verify answers "
    "Internal Server Error instead of issuing the session"
)


@pytest.mark.skip(reason=RED_REASON)
class TestLastAttemptSuccessAcceptance(AbstractBackendTest):
    """Сценарий 5.5: верный код на последней разрешённой попытке всё ещё выдаёт сессию.

    Дано пользователь получил рабочий код
    И пользователь уже потратил все попытки кроме последней на неверный код
    Когда пользователь отправляет верный код на проверку последней разрешённой попыткой
    Тогда выдаётся сессия
    И следующая проверка тем же кодом отклоняется как неудачная авторизация
    """

    async def test_should_issue_a_session_when_the_correct_code_arrives_on_the_last_allowed_attempt(
        self, last_attempt_success_statements: LastAttemptSuccessStatements
    ):
        working = await last_attempt_success_statements.given_user_holding_a_working_code()
        await last_attempt_success_statements.spend_every_attempt_but_the_last(working)

        session = await last_attempt_success_statements.verify_the_correct_code(working)

        last_attempt_success_statements.assert_session_was_issued(session)
        rejected = await last_attempt_success_statements.verify_the_same_code_again(working)
        last_attempt_success_statements.assert_rejected_as_failed_authorization(rejected)
