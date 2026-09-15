import pytest
from statements.concurrent_verify_statements import ConcurrentVerifyStatements

from tests.backend.abstract_backend_test import AbstractBackendTest


@pytest.mark.skip(
    reason="RED: two simultaneous verifications answer [200, 500] — the losing call reads a redeemed challenge "
    "and no replay record is consulted, so it fails instead of returning the session already issued"
)
class TestConcurrentVerifyAcceptance(AbstractBackendTest):
    """Сценарий 7.2: два одновременных верных кода дают ровно одну сессию.

    Дано пользователь получил рабочий код
    Когда две проверки с одной и той же парой «идентификатор challenge и код» доведены до управляемой точки
    синхронизации внутри окна между гашением challenge и записью о повторе и отпущены вместе
    Тогда оба ответа успешны и несут один и тот же идентификатор сессии
    И в хранилище лежит ровно одна сессия
    И проигравший не получает отказ «challenge не существует»
    """

    async def test_should_answer_two_simultaneous_verifications_with_one_and_the_same_session(
        self, concurrent_verify_statements: ConcurrentVerifyStatements
    ):
        registered = await concurrent_verify_statements.given_a_user_holding_a_working_code()

        outcomes = await concurrent_verify_statements.release_two_verifications_of_the_same_code_together(registered)

        concurrent_verify_statements.assert_both_answers_are_successful_and_carry_the_same_session(outcomes, registered)
        await concurrent_verify_statements.assert_exactly_one_session_is_stored(outcomes, registered)
        concurrent_verify_statements.assert_no_answer_refuses_the_challenge_as_missing(outcomes)
