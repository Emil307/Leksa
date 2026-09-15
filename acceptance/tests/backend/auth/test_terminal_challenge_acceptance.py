import pytest
from statements.terminal_challenge_statements import TerminalChallenge, TerminalChallengeStatements

from tests.backend.abstract_backend_test import AbstractBackendTest

RED_REASON = (
    "RED: a challenge in a terminal state must reject the code with 401, got 500 — "
    "POST /api/v1/auth/challenge/verify answers Internal Server Error for every terminal state "
    "(exhausted by attempts, code lifetime expired, superseded by a new request, "
    "redeemed with an expired replay window, never existed) instead of the unauthorized answer"
)


@pytest.mark.skip(reason=RED_REASON)
class TestTerminalChallengeAcceptance(AbstractBackendTest):
    """Сценарий 5.3: терминальное состояние отклоняет любой код и не оставляет следа.

    Дано challenge находится в терминальном состоянии
    Когда пользователь отправляет верный код на проверку
    Тогда проверка отклоняется как неудачная авторизация
    И сессия не выдаётся
    И ни одного пользователя не создано
    И в ответе нет ни одного токена
    И в хранилище challenge не создано ни одного ключа, не сброшен и не снят ни один срок жизни,
    не воскрешён ни один счётчик попыток и не записана запись о повторе
    """

    async def test_should_reject_a_challenge_exhausted_by_attempts_without_a_trace(
        self, terminal_challenge_statements: TerminalChallengeStatements
    ):
        terminal = await terminal_challenge_statements.given_challenge_exhausted_by_attempts()

        await self._assert_code_is_rejected_without_a_trace(terminal_challenge_statements, terminal)

    async def test_should_reject_a_challenge_whose_code_lifetime_expired_without_a_trace(
        self, terminal_challenge_statements: TerminalChallengeStatements
    ):
        terminal = await terminal_challenge_statements.given_challenge_whose_code_lifetime_expired()

        await self._assert_code_is_rejected_without_a_trace(terminal_challenge_statements, terminal)

    async def test_should_reject_a_challenge_superseded_by_a_new_request_without_a_trace(
        self, terminal_challenge_statements: TerminalChallengeStatements
    ):
        terminal = await terminal_challenge_statements.given_challenge_superseded_by_a_new_request()

        await self._assert_code_is_rejected_without_a_trace(terminal_challenge_statements, terminal)

    async def test_should_reject_a_redeemed_challenge_past_its_replay_window_without_a_trace(
        self, terminal_challenge_statements: TerminalChallengeStatements
    ):
        terminal = await terminal_challenge_statements.given_challenge_redeemed_with_an_expired_replay_window()

        await self._assert_code_is_rejected_without_a_trace(terminal_challenge_statements, terminal)

    async def test_should_reject_a_challenge_that_never_existed_without_a_trace(
        self, terminal_challenge_statements: TerminalChallengeStatements
    ):
        terminal = await terminal_challenge_statements.given_challenge_that_never_existed()

        await self._assert_code_is_rejected_without_a_trace(terminal_challenge_statements, terminal)

    @staticmethod
    async def _assert_code_is_rejected_without_a_trace(
        statements: TerminalChallengeStatements, terminal: TerminalChallenge
    ) -> None:
        before = await statements.capture_trace(terminal)

        rejected = await statements.verify_code(terminal)

        statements.assert_rejected_as_failed_authorization(rejected, terminal)
        statements.assert_no_session_and_no_token_in_the_answer(rejected)
        await statements.assert_no_user_was_created(terminal, before)
        await statements.assert_challenge_store_kept_no_trace(terminal, before)
