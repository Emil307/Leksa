from statements.server_owned_fields_statements import ServerOwnedFieldsStatements

from tests.backend.abstract_backend_test import AbstractBackendTest


class TestServerOwnedFieldsAcceptance(AbstractBackendTest):
    """Сценарий 2.1: серверные поля, присланные клиентом, игнорируются.

    Дано в системе нет живого challenge
    Когда клиент отправляет запрос, в теле которого дополнительно прислано серверное поле
    Тогда запрос обрабатывается штатно
    И побеждает значение, сгенерированное сервером
    И присланное значение не попало ни в ответ, ни в хранилище
    """

    async def test_should_ignore_server_owned_fields_planted_in_the_code_request(
        self, server_owned_fields_statements: ServerOwnedFieldsStatements
    ):
        planted = await server_owned_fields_statements.request_code_with_server_fields()

        server_owned_fields_statements.assert_start_answers_only_server_generated_values(planted)
        await server_owned_fields_statements.assert_stored_challenge_belongs_to_the_requested_address(planted)

    async def test_should_ignore_server_owned_fields_planted_in_the_verify_request(
        self, server_owned_fields_statements: ServerOwnedFieldsStatements
    ):
        planted = await server_owned_fields_statements.verify_code_with_server_fields()

        server_owned_fields_statements.assert_session_is_the_server_generated_one(planted)
        await server_owned_fields_statements.assert_identity_comes_from_the_stored_challenge(planted)
