from statements.hostile_email_statements import HostileEmailStatements

from tests.backend.abstract_backend_test import AbstractBackendTest


class TestHostileEmailAcceptance(AbstractBackendTest):
    """Сценарий 1.4: враждебный email не рвёт лог и не пересекается с чужим ключом.

    Дано адрес содержит враждебную часть
    Когда клиент запрашивает код на этот адрес
    Тогда либо запрос отклоняется как некорректные данные, либо адрес попадает в заявку
    ровно тем значением, которое пришло
    И строка лога не разрывается на две
    И ключ хранилища этого адреса не совпадает с ключом другого адреса
    И маска адреса в логе остаётся корректным текстом — без символа замены и без
    разорванной последовательности
    """

    async def test_should_reject_an_address_carrying_a_line_break_without_splitting_it_in_two(
        self, hostile_email_statements: HostileEmailStatements
    ):
        attempt = hostile_email_statements.address_carrying_a_line_break()

        outcome = await hostile_email_statements.request_code_for(attempt.offered)

        hostile_email_statements.assert_rejected_as_invalid_data(outcome)
        await hostile_email_statements.assert_no_request_was_queued_for(
            attempt.offered, attempt.head, attempt.injected_tail
        )
        await hostile_email_statements.assert_address_holds_no_storage_key(attempt.head)
        await hostile_email_statements.assert_address_holds_no_storage_key(attempt.injected_tail)

    async def test_should_key_a_multibyte_address_apart_from_its_lookalikes(
        self, hostile_email_statements: HostileEmailStatements
    ):
        addresses = hostile_email_statements.multibyte_addresses_around_the_masking_boundary()

        accepted = await hostile_email_statements.request_code_for(addresses.address)

        hostile_email_statements.assert_accepted(accepted)
        await hostile_email_statements.assert_request_was_queued_verbatim_for(addresses.address)
        await hostile_email_statements.assert_the_queue_carries_no_mangled_spelling(addresses)
        await hostile_email_statements.assert_address_is_on_its_own_cooldown(addresses.address)
        await hostile_email_statements.assert_address_holds_no_storage_key(addresses.lookalike)
        await hostile_email_statements.assert_address_holds_no_storage_key(addresses.folded)
        await hostile_email_statements.assert_request_was_queued_verbatim_for(addresses.lookalike)
        await hostile_email_statements.assert_request_was_queued_verbatim_for(addresses.folded)
