import pytest
from clients.application.profile_client import ProfileClient
from statements.auth_database import AuthDatabase
from statements.jwt_trust_statements import JwtTrustStatements

from tests.backend.abstract_backend_test import AbstractBackendTest


@pytest.fixture
def jwt_trust_statements(profile_client: ProfileClient, auth_database: AuthDatabase) -> JwtTrustStatements:
    return JwtTrustStatements(profile_client, auth_database)


class TestJwtTrustAcceptance(AbstractBackendTest):
    """Сценарий 2.1: сервер принимает только доверенный HS256 JWT.

    Дано существует пользователь с действующей сессией
    Когда клиент запрашивает профиль с вариантом токена <вариант>
    Тогда запрос имеет исход <исход>
    И отказ дословно совпадает с единым отказом авторизации
    """

    async def test_should_return_profile_for_hs256_token_signed_with_the_server_secret(
        self, jwt_trust_statements: JwtTrustStatements
    ):
        user = await jwt_trust_statements.sign_in_user_with_live_session()

        response = await jwt_trust_statements.request_profile_with(user.access_token)

        jwt_trust_statements.assert_profile_returned(response, user)

    async def test_should_refuse_token_with_a_tampered_signature(self, jwt_trust_statements: JwtTrustStatements):
        user = await jwt_trust_statements.sign_in_user_with_live_session()

        response = await jwt_trust_statements.request_profile_with(
            jwt_trust_statements.token_with_tampered_signature(user)
        )

        jwt_trust_statements.assert_matches_unified_authorization_refusal(response)

    async def test_should_refuse_token_signed_with_a_foreign_secret(self, jwt_trust_statements: JwtTrustStatements):
        user = await jwt_trust_statements.sign_in_user_with_live_session()

        response = await jwt_trust_statements.request_profile_with(
            jwt_trust_statements.token_signed_with_a_foreign_secret(user)
        )

        jwt_trust_statements.assert_matches_unified_authorization_refusal(response)

    async def test_should_refuse_token_signed_with_another_algorithm(self, jwt_trust_statements: JwtTrustStatements):
        user = await jwt_trust_statements.sign_in_user_with_live_session()

        response = await jwt_trust_statements.request_profile_with(
            jwt_trust_statements.token_signed_with_another_algorithm(user)
        )

        jwt_trust_statements.assert_matches_unified_authorization_refusal(response)

    async def test_should_refuse_token_without_a_signing_algorithm(self, jwt_trust_statements: JwtTrustStatements):
        user = await jwt_trust_statements.sign_in_user_with_live_session()

        response = await jwt_trust_statements.request_profile_with(
            jwt_trust_statements.token_without_a_signing_algorithm(user)
        )

        jwt_trust_statements.assert_matches_unified_authorization_refusal(response)
