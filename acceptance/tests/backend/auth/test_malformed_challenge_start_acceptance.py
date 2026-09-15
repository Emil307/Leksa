from statements.malformed_challenge_start_statements import MalformedChallengeStartStatements

from tests.backend.abstract_backend_test import AbstractBackendTest


class TestMalformedChallengeStartAcceptance(AbstractBackendTest):
    """Сценарий 1.1: некорректное тело запроса кода отклоняется до постановки заявки в очередь.

    Дано в системе нет живого challenge и нет заявок в очереди
    Когда клиент запрашивает код, в теле которого поле имеет некорректное значение
    Тогда запрос отклоняется как некорректные данные
    И заявка в очередь не кладётся
    И живой challenge не создаётся
    """

    async def test_should_reject_a_body_without_the_email_field(
        self, malformed_challenge_start_statements: MalformedChallengeStartStatements
    ):
        rejection = await malformed_challenge_start_statements.request_code_without_the_email_field()

        malformed_challenge_start_statements.assert_rejected_as_invalid_data(rejection)
        await malformed_challenge_start_statements.assert_no_request_was_queued(rejection)

    async def test_should_reject_a_body_whose_email_is_null(
        self, malformed_challenge_start_statements: MalformedChallengeStartStatements
    ):
        rejection = await malformed_challenge_start_statements.request_code_with_a_null_email()

        malformed_challenge_start_statements.assert_rejected_as_invalid_data(rejection)
        await malformed_challenge_start_statements.assert_no_request_was_queued(rejection)

    async def test_should_reject_a_body_whose_email_is_empty(
        self, malformed_challenge_start_statements: MalformedChallengeStartStatements
    ):
        rejection = await malformed_challenge_start_statements.request_code_with_an_empty_email()

        malformed_challenge_start_statements.assert_rejected_as_invalid_data(rejection)
        await malformed_challenge_start_statements.assert_no_request_was_queued(rejection)

    async def test_should_reject_an_email_without_an_at_sign(
        self, malformed_challenge_start_statements: MalformedChallengeStartStatements
    ):
        rejection = await malformed_challenge_start_statements.request_code_with_an_email_without_an_at_sign()

        malformed_challenge_start_statements.assert_rejected_as_invalid_data(rejection)
        await malformed_challenge_start_statements.assert_no_request_was_queued(rejection)

    async def test_should_reject_an_email_without_a_domain_part(
        self, malformed_challenge_start_statements: MalformedChallengeStartStatements
    ):
        rejection = await malformed_challenge_start_statements.request_code_with_an_email_without_a_domain_part()

        malformed_challenge_start_statements.assert_rejected_as_invalid_data(rejection)
        await malformed_challenge_start_statements.assert_no_request_was_queued(rejection)

    async def test_should_reject_a_body_without_the_challenge_type_field(
        self, malformed_challenge_start_statements: MalformedChallengeStartStatements
    ):
        rejection = await malformed_challenge_start_statements.request_code_without_the_challenge_type_field()

        malformed_challenge_start_statements.assert_rejected_as_invalid_data(rejection)
        await malformed_challenge_start_statements.assert_no_request_was_queued(rejection)
        await malformed_challenge_start_statements.assert_no_live_challenge_holds_the_offered_email(rejection)

    async def test_should_reject_a_body_whose_challenge_type_is_null(
        self, malformed_challenge_start_statements: MalformedChallengeStartStatements
    ):
        rejection = await malformed_challenge_start_statements.request_code_with_a_null_challenge_type()

        malformed_challenge_start_statements.assert_rejected_as_invalid_data(rejection)
        await malformed_challenge_start_statements.assert_no_request_was_queued(rejection)
        await malformed_challenge_start_statements.assert_no_live_challenge_holds_the_offered_email(rejection)

    async def test_should_reject_a_body_whose_challenge_type_is_empty(
        self, malformed_challenge_start_statements: MalformedChallengeStartStatements
    ):
        rejection = await malformed_challenge_start_statements.request_code_with_an_empty_challenge_type()

        malformed_challenge_start_statements.assert_rejected_as_invalid_data(rejection)
        await malformed_challenge_start_statements.assert_no_request_was_queued(rejection)
        await malformed_challenge_start_statements.assert_no_live_challenge_holds_the_offered_email(rejection)

    async def test_should_reject_an_unknown_challenge_type(
        self, malformed_challenge_start_statements: MalformedChallengeStartStatements
    ):
        rejection = await malformed_challenge_start_statements.request_code_with_an_unknown_challenge_type()

        malformed_challenge_start_statements.assert_rejected_as_invalid_data(rejection)
        await malformed_challenge_start_statements.assert_no_request_was_queued(rejection)
        await malformed_challenge_start_statements.assert_no_live_challenge_holds_the_offered_email(rejection)
