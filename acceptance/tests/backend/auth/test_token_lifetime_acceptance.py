from statements.token_lifetime_statements import TokenLifetimeStatements

from tests.backend.abstract_backend_test import AbstractBackendTest


class TestTokenLifetimeAcceptance(AbstractBackendTest):
    """Сценарий 8.1: время жизни проходит от конфигурации до сроков токенов без искажений.

    Дано время жизни кода и сроки токенов заданы конфигурацией
    Когда пользователь запрашивает код и входит по нему
    Тогда момент истечения из ответа равен моменту запроса плюс настроенное время жизни кода
    И проверка до момента истечения успешна
    И срок access-токена равен моменту выдачи плюс настроенный срок access-токена
    И срок созданной строки сессии равен моменту выдачи плюс настроенный срок refresh-токена
    """

    async def test_code_expiry_is_the_request_instant_plus_the_configured_code_lifetime(
        self, token_lifetime_statements: TokenLifetimeStatements
    ):
        requested = await token_lifetime_statements.given_requested_code()

        token_lifetime_statements.assert_code_expiry_is_request_instant_plus_configured_lifetime(requested)

    async def test_verification_before_the_code_expiry_is_accepted(
        self, token_lifetime_statements: TokenLifetimeStatements
    ):
        requested = await token_lifetime_statements.given_requested_code()

        issued = await token_lifetime_statements.verify_before_expiry(requested)

        token_lifetime_statements.assert_verification_accepted(issued)

    async def test_access_token_expiry_is_the_issue_instant_plus_the_configured_access_lifetime(
        self, token_lifetime_statements: TokenLifetimeStatements
    ):
        requested = await token_lifetime_statements.given_requested_code()

        issued = await token_lifetime_statements.verify_before_expiry(requested)

        token_lifetime_statements.assert_verification_accepted(issued)
        token_lifetime_statements.assert_access_expiry_is_issue_instant_plus_configured_access_lifetime(issued)

    async def test_session_row_expiry_is_the_issue_instant_plus_the_configured_refresh_lifetime(
        self, token_lifetime_statements: TokenLifetimeStatements
    ):
        requested = await token_lifetime_statements.given_requested_code()

        issued = await token_lifetime_statements.verify_before_expiry(requested)

        token_lifetime_statements.assert_verification_accepted(issued)
        await token_lifetime_statements.assert_session_row_expiry_is_issue_instant_plus_configured_refresh_lifetime(
            issued
        )
