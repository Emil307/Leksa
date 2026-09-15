import pytest
from clients.application.profile_client import ProfileClient
from statements.auth_database import AuthDatabase
from statements.authorization_header_statements import AuthorizationHeaderStatements

from tests.backend.abstract_backend_test import AbstractBackendTest


@pytest.fixture
def authorization_header_statements(
    profile_client: ProfileClient, auth_database: AuthDatabase
) -> AuthorizationHeaderStatements:
    return AuthorizationHeaderStatements(profile_client, auth_database)


class TestAuthorizationHeaderLimitAcceptance(AbstractBackendTest):
    """Сценарий 1.1: лимит Authorization считается по wire bytes до разбора JWT.

    Дано существует пользователь с действующей сессией
    Когда клиент запрашивает профиль с заголовком авторизации длиной <длина>
    Тогда запрос имеет исход <исход>
    И заголовок за границей отклоняется до проверки сессии
    """

    async def test_should_return_profile_at_exactly_the_wire_byte_limit(
        self, authorization_header_statements: AuthorizationHeaderStatements
    ):
        user = await authorization_header_statements.sign_in_user()
        credential = authorization_header_statements.credential_at_the_wire_byte_limit(user)

        probe = await authorization_header_statements.request_profile_with(credential)

        authorization_header_statements.assert_profile_of_owner_returned(probe, user)

    async def test_should_refuse_one_wire_byte_past_the_limit_before_checking_the_session(
        self, authorization_header_statements: AuthorizationHeaderStatements
    ):
        user = await authorization_header_statements.sign_in_user()
        credential = authorization_header_statements.credential_one_wire_byte_past_the_limit(user)

        probe = await authorization_header_statements.request_profile_with(credential)

        authorization_header_statements.assert_unified_authorization_refusal(probe)

    async def test_should_refuse_multibyte_header_below_the_code_point_limit(
        self, authorization_header_statements: AuthorizationHeaderStatements
    ):
        await authorization_header_statements.sign_in_user()
        credential = authorization_header_statements.credential_with_more_octets_than_code_points()

        probe = await authorization_header_statements.request_profile_with(credential)

        authorization_header_statements.assert_unified_authorization_refusal(probe)
