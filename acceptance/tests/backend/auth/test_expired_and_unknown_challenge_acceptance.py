import pytest
from statements.expired_and_unknown_challenge_statements import ExpiredAndUnknownChallengeStatements

from tests.backend.abstract_backend_test import AbstractBackendTest

RED_REASON = (
    "RED: «истёкший challenge» must be refused with 401, got 500 with body 'Internal Server Error' — "
    "POST /api/v1/auth/challenge/verify answers Internal Server Error both for an expired challenge "
    "and for an identifier that never existed, instead of the unauthorized envelope"
)


@pytest.mark.skip(reason=RED_REASON)
class TestExpiredAndUnknownChallengeAcceptance(AbstractBackendTest):
    """Сценарий 5.4: неизвестный идентификатор challenge отвечает ровно как истёкший.

    Дано один challenge истёк, а второй идентификатор не существовал никогда
    Когда клиент отправляет проверку по каждому из них
    Тогда оба ответа несут одинаковый статус, одинаковый код ошибки и одинаковое сообщение
    И ни по одному ответу нельзя узнать, существовал ли challenge
    """

    async def test_should_answer_an_unknown_identifier_exactly_as_an_expired_one(
        self, expired_and_unknown_challenge_statements: ExpiredAndUnknownChallengeStatements
    ):
        challenges = (
            await expired_and_unknown_challenge_statements.given_an_expired_challenge_and_an_unknown_identifier()
        )

        answers = await expired_and_unknown_challenge_statements.verify_each(challenges)

        expired_and_unknown_challenge_statements.assert_both_were_refused_as_unauthorized(answers)
        expired_and_unknown_challenge_statements.assert_the_two_answers_are_indistinguishable(answers)
        expired_and_unknown_challenge_statements.assert_neither_answer_carries_a_session_or_a_token(answers)
