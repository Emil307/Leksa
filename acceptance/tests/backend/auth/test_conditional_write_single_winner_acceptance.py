from statements.conditional_write_single_winner_statements import ConditionalWriteSingleWinnerStatements

from tests.backend.abstract_backend_test import AbstractBackendTest


class TestConditionalWriteSingleWinnerAcceptance(AbstractBackendTest):
    """Интеграция 1.2: условная запись разрешает только одного конкурентного победителя.

    Дано две независимые операции хранилища используют один исходный refresh-токен
    Когда их условные обновления выполняются с детерминированным чередованием
    Тогда одна операция изменяет одну строку
    И вторая операция не изменяет строк
    И сохранённые токен и срок принадлежат одной полной ротации победителя
    """

    async def test_should_let_exactly_one_operation_change_one_row_and_refuse_the_other(
        self, conditional_write_single_winner_statements: ConditionalWriteSingleWinnerStatements
    ):
        live = await conditional_write_single_winner_statements.given_live_session_presented_by_two_operations()

        race = await conditional_write_single_winner_statements.release_both_conditional_updates_together(live)

        conditional_write_single_winner_statements.assert_exactly_one_operation_changed_one_row(race)
        conditional_write_single_winner_statements.assert_the_other_operation_changed_no_row(race)

    async def test_should_store_the_full_rotation_of_the_winner_only(
        self, conditional_write_single_winner_statements: ConditionalWriteSingleWinnerStatements
    ):
        live = await conditional_write_single_winner_statements.given_live_session_presented_by_two_operations()

        race = await conditional_write_single_winner_statements.release_both_conditional_updates_together(live)

        conditional_write_single_winner_statements.assert_exactly_one_operation_changed_one_row(race)
        conditional_write_single_winner_statements.assert_stored_token_and_expiry_belong_to_the_winner(race)
