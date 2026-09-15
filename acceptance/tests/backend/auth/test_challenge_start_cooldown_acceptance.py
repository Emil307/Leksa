from statements.challenge_start_cooldown_statements import ChallengeStartCooldownStatements

from tests.backend.abstract_backend_test import AbstractBackendTest


class TestChallengeStartCooldownAcceptance(AbstractBackendTest):
    """Сценарий 2.4: повторный запрос внутри кулдауна отклоняется и второй заявки не создаёт.

    Дано пользователь только что запросил код на свой email
    Когда клиент запрашивает код на тот же email, не дожидаясь конца кулдауна
    Тогда запрос отклоняется по кулдауну
    И ответ несёт остаток ожидания целыми секундами
    И вторая заявка в очередь не кладётся
    И ранее выданный код по-прежнему выдаёт сессию
    """

    async def test_should_reject_the_repeat_request_without_queueing_a_second_email(
        self, challenge_start_cooldown_statements: ChallengeStartCooldownStatements
    ):
        email, requested = await challenge_start_cooldown_statements.given_user_just_requested_a_code()

        denial = await challenge_start_cooldown_statements.request_code_again(email)

        challenge_start_cooldown_statements.assert_rejected_by_cooldown(denial)
        challenge_start_cooldown_statements.assert_carries_remaining_wait_in_whole_seconds(denial)
        await challenge_start_cooldown_statements.assert_single_queued_request(email)
        await challenge_start_cooldown_statements.assert_earlier_code_still_issues_a_session(requested)

    async def test_should_keep_counting_the_remaining_wait_down_on_every_repeat(
        self, challenge_start_cooldown_statements: ChallengeStartCooldownStatements
    ):
        email, _ = await challenge_start_cooldown_statements.given_user_just_requested_a_code()

        earlier = await challenge_start_cooldown_statements.request_code_again(email)
        later = await challenge_start_cooldown_statements.request_code_again(email)

        challenge_start_cooldown_statements.assert_rejected_by_cooldown(later)
        challenge_start_cooldown_statements.assert_carries_remaining_wait_in_whole_seconds(earlier)
        challenge_start_cooldown_statements.assert_carries_remaining_wait_in_whole_seconds(later)
        challenge_start_cooldown_statements.assert_remaining_wait_does_not_grow(earlier, later)
        await challenge_start_cooldown_statements.assert_single_queued_request(email)
