from statements.auth_statements import AuthStatements

from tests.backend.abstract_backend_test import AbstractBackendTest


class TestChallengeStartAcceptance(AbstractBackendTest):
    """Сценарий 2.1: запрос кода возвращает challenge.

    Дано в системе нет живого challenge для этого email
    Когда клиент запрашивает код на свой email
    Тогда ответ несёт идентификатор challenge, его тип и момент истечения
    И момент истечения равен моменту создания плюс настроенное время жизни кода
    И в ответе нет ни кода, ни адреса перехода, ни состояния challenge
    """

    async def test_should_return_a_challenge_with_identifier_type_and_configured_expiry(
        self, auth_statements: AuthStatements
    ):
        email = auth_statements.new_user_email()

        challenge = await auth_statements.request_code(email)

        auth_statements.assert_challenge_carries_identifier_and_type(challenge)
        auth_statements.assert_expiry_is_creation_plus_configured_code_lifetime(challenge)
        auth_statements.assert_response_carries_no_code_no_authorize_url_and_no_status(challenge)
