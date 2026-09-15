from statements.unregistered_challenge_strategy_statements import UnregisteredChallengeStrategyStatements

from tests.backend.abstract_backend_test import AbstractBackendTest


class TestUnregisteredChallengeStrategyAcceptance(AbstractBackendTest):
    """Сценарий 2.2: тип challenge без зарегистрированной стратегии отклоняется явно.

    Дано в перечислении типов challenge есть значение, для которого стратегия не зарегистрирована
    Когда клиент запрашивает код с этим типом
    Тогда запрос отклоняется явной ошибкой
    И ветка по умолчанию не выбирается
    И заявка в очередь не кладётся
    """

    async def test_should_reject_a_challenge_type_that_has_no_registered_strategy(
        self, unregistered_challenge_strategy_statements: UnregisteredChallengeStrategyStatements
    ):
        rejection = await unregistered_challenge_strategy_statements.request_code_with_a_type_without_a_strategy()

        unregistered_challenge_strategy_statements.assert_rejected_with_an_explicit_error(rejection)
        unregistered_challenge_strategy_statements.assert_no_challenge_was_handed_out(rejection)
        await unregistered_challenge_strategy_statements.assert_no_request_was_queued(rejection)
        await unregistered_challenge_strategy_statements.assert_the_address_stayed_free_for_a_registered_type(rejection)

    async def test_should_not_fall_back_to_the_registered_strategy_for_a_lowercase_spelling(
        self, unregistered_challenge_strategy_statements: UnregisteredChallengeStrategyStatements
    ):
        rejection = await unregistered_challenge_strategy_statements.request_code_with_a_lowercase_registered_type()

        unregistered_challenge_strategy_statements.assert_rejected_with_an_explicit_error(rejection)
        unregistered_challenge_strategy_statements.assert_no_challenge_was_handed_out(rejection)
        await unregistered_challenge_strategy_statements.assert_no_request_was_queued(rejection)
        await unregistered_challenge_strategy_statements.assert_the_address_stayed_free_for_a_registered_type(rejection)
