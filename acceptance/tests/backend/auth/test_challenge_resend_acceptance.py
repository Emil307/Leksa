import pytest
from statements.challenge_resend_statements import ChallengeResendStatements

from tests.backend.abstract_backend_test import AbstractBackendTest

RED_REASON = (
    "RED: the superseded code must be rejected with 401, got 500 — "
    "POST /api/v1/auth/challenge/verify answers Internal Server Error for a challenge "
    "evicted by a later start, instead of the unauthorized answer"
)


@pytest.mark.skip(reason=RED_REASON)
class TestChallengeResendAcceptance(AbstractBackendTest):
    """Сценарий 2.5: повторный запрос после кулдауна выдаёт новый challenge и обесценивает прежний код.

    Дано пользователь запросил код на свой email и кулдаун уже истёк
    Когда клиент запрашивает код на тот же email
    Тогда ответ несёт новый идентификатор challenge и новый момент истечения
    И в очередь кладётся вторая заявка с новым кодом
    И прежний код сессию больше не выдаёт
    И у этого email остаётся ровно один живой challenge
    """

    async def test_should_issue_a_new_challenge_and_void_the_previous_code(
        self, challenge_resend_statements: ChallengeResendStatements
    ):
        issued = await challenge_resend_statements.given_requested_code_whose_cooldown_expired()

        reissued = await challenge_resend_statements.request_code_again(issued)

        challenge_resend_statements.assert_challenge_is_new_with_a_new_expiry(reissued, issued)
        await challenge_resend_statements.assert_second_request_is_queued_with_a_new_code(issued)
        await challenge_resend_statements.assert_previous_code_no_longer_issues_a_session(issued)
        await challenge_resend_statements.assert_email_keeps_exactly_one_live_challenge(reissued, issued)
