from statements.access_token_algorithm_and_claims_statements import AccessTokenAlgorithmAndClaimsStatements

from tests.backend.abstract_backend_test import AbstractBackendTest


class TestAccessTokenAlgorithmAndClaimsAcceptance(AbstractBackendTest):
    """Безопасность 3.1: новый access-токен имеет только разрешённый алгоритм и claims.

    Дано существует действующая сессия с фиксированным временем
    Когда клиент обновляет токены этой сессии
    Тогда новый access-токен подписан разрешённым алгоритмом
    И подпись проверяется настроенным секретом
    И токен содержит прежние идентификаторы пользователя и сессии
    И токен содержит точный срок действия и не содержит лишних claims
    """

    async def test_should_sign_the_new_access_token_with_hs256_under_the_configured_secret(
        self, access_token_algorithm_and_claims_statements: AccessTokenAlgorithmAndClaimsStatements
    ):
        session = await access_token_algorithm_and_claims_statements.given_live_session()

        rotation = await access_token_algorithm_and_claims_statements.rotate_tokens(session)

        access_token_algorithm_and_claims_statements.assert_new_access_token_is_signed_with_hs256(rotation)
        access_token_algorithm_and_claims_statements.assert_signature_verifies_with_the_configured_secret(rotation)

    async def test_should_carry_previous_identifiers_exact_expiry_and_no_extra_claims(
        self, access_token_algorithm_and_claims_statements: AccessTokenAlgorithmAndClaimsStatements
    ):
        session = await access_token_algorithm_and_claims_statements.given_live_session()

        rotation = await access_token_algorithm_and_claims_statements.rotate_tokens(session)

        access_token_algorithm_and_claims_statements.assert_token_names_the_previous_user_and_session(rotation)
        access_token_algorithm_and_claims_statements.assert_token_carries_exact_expiry(rotation)
        access_token_algorithm_and_claims_statements.assert_token_carries_no_extra_claims(rotation)

    async def test_should_refuse_the_rotated_token_after_algorithm_substitution(
        self, access_token_algorithm_and_claims_statements: AccessTokenAlgorithmAndClaimsStatements
    ):
        session = await access_token_algorithm_and_claims_statements.given_live_session()
        rotation = await access_token_algorithm_and_claims_statements.rotate_tokens(session)

        response = await access_token_algorithm_and_claims_statements.request_profile_with_substituted_algorithm(
            rotation
        )

        access_token_algorithm_and_claims_statements.assert_matches_unified_authorization_refusal(response)
