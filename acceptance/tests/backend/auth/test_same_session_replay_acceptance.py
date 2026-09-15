import pytest
from statements.same_session_replay_statements import SameSessionReplayStatements

from tests.backend.abstract_backend_test import AbstractBackendTest

RED_REASON = (
    "RED: the replayed verification must be accepted with 200, got 500 — "
    "POST /api/v1/auth/challenge/verify answers Internal Server Error when the same challengeId and code "
    "are repeated inside the replay window, instead of returning the very session the first verification opened"
)


@pytest.mark.skip(reason=RED_REASON)
class TestSameSessionReplayAcceptance(AbstractBackendTest):
    """Сценарий 6.1: повтор внутри окна возвращает ту же сессию.

    Дано пользователь только что вошёл по коду и получил сессию
    Когда клиент повторяет ту же пару «идентификатор challenge и код» внутри окна повтора
    Тогда ответ несёт тот же идентификатор сессии и тот же refresh-токен
    И access-токен подписан заново
    И в хранилище лежит ровно одна сессия этого пользователя
    """

    async def test_should_answer_the_replay_with_the_very_same_session(
        self, same_session_replay_statements: SameSessionReplayStatements
    ):
        first = await same_session_replay_statements.given_a_user_who_just_logged_in_with_a_code()

        replay = await same_session_replay_statements.repeat_the_same_challenge_and_code(first)

        same_session_replay_statements.assert_the_same_session_identifier_and_refresh_token(first, replay)
        same_session_replay_statements.assert_the_access_token_is_signed_anew(first, replay)
        await same_session_replay_statements.assert_exactly_one_session_of_the_user(first)
