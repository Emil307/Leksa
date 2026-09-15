import pytest
from statements.declared_input_limits_statements import DeclaredInputLimitsStatements

from tests.backend.abstract_backend_test import AbstractBackendTest


class TestDeclaredInputLimitsAcceptance(AbstractBackendTest):
    """Сценарий безопасности 1.1: ввод сверх объявленных границ отклоняется до постановки заявки.

    Дано в системе нет живого challenge и нет заявок в очереди
    Когда клиент отправляет <ввод>
    Тогда запрос отклоняется как некорректные данные
    И заявка в очередь не кладётся
    И живой challenge не создаётся
    """

    async def test_should_reject_an_email_of_255_octets_when_the_declared_limit_is_254(
        self, declared_input_limits_statements: DeclaredInputLimitsStatements
    ):
        rejection = await declared_input_limits_statements.request_code_with_an_email_of_255_octets()

        declared_input_limits_statements.assert_rejected_as_invalid_data(rejection)
        await declared_input_limits_statements.assert_no_request_was_queued(rejection)
        declared_input_limits_statements.assert_no_live_challenge_was_created(rejection)

    async def test_should_reject_a_multibyte_email_that_fits_254_characters_but_not_254_octets(
        self, declared_input_limits_statements: DeclaredInputLimitsStatements
    ):
        rejection = await declared_input_limits_statements.request_code_with_a_multibyte_email_over_the_octet_limit()

        declared_input_limits_statements.assert_rejected_as_invalid_data(rejection)
        await declared_input_limits_statements.assert_no_request_was_queued(rejection)
        declared_input_limits_statements.assert_no_live_challenge_was_created(rejection)

    async def test_should_reject_a_code_request_body_of_several_megabytes(
        self, declared_input_limits_statements: DeclaredInputLimitsStatements
    ):
        rejection = await declared_input_limits_statements.request_code_with_a_body_of_several_megabytes()

        declared_input_limits_statements.assert_rejected_as_invalid_data(rejection)
        await declared_input_limits_statements.assert_no_request_was_queued(rejection)
        declared_input_limits_statements.assert_no_live_challenge_was_created(rejection)
        await declared_input_limits_statements.assert_a_valid_request_is_still_accepted()

    @pytest.mark.skip(
        reason="RED: код из 7 цифр при неизвестном challengeId отвечает 500 с пустым телом вместо 400 VALIDATION_FAILED"
    )
    async def test_should_reject_a_code_of_seven_digits_on_verify(
        self, declared_input_limits_statements: DeclaredInputLimitsStatements
    ):
        rejection = await declared_input_limits_statements.verify_a_code_of_seven_digits()

        declared_input_limits_statements.assert_rejected_as_invalid_data(rejection)
        declared_input_limits_statements.assert_carries_neither_session_nor_token(rejection)
        declared_input_limits_statements.assert_no_live_challenge_was_created(rejection)

    async def test_should_reject_a_verify_body_of_several_megabytes(
        self, declared_input_limits_statements: DeclaredInputLimitsStatements
    ):
        rejection = await declared_input_limits_statements.verify_with_a_body_of_several_megabytes()

        declared_input_limits_statements.assert_rejected_as_invalid_data(rejection)
        declared_input_limits_statements.assert_carries_neither_session_nor_token(rejection)
        declared_input_limits_statements.assert_no_live_challenge_was_created(rejection)
        await declared_input_limits_statements.assert_a_valid_request_is_still_accepted()
