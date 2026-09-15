import pytest
from clients.application.profile_client import ProfileClient
from statements.auth_database import AuthDatabase
from statements.profile_auth_refusal_statements import AUTHORIZATION_VARIANTS, ProfileAuthRefusalStatements
from statements.profile_statements import ProfileStatements

from tests.backend.abstract_backend_test import AbstractBackendTest


@pytest.fixture
def profile_auth_refusal_statements(
    profile_client: ProfileClient,
    profile_statements: ProfileStatements,
    auth_database: AuthDatabase,
) -> ProfileAuthRefusalStatements:
    return ProfileAuthRefusalStatements(profile_client, profile_statements, auth_database)


class TestProfileAuthorizationRefusalAcceptance(AbstractBackendTest):
    """Сценарий 2.1: запрос профиля с невалидной авторизацией отклоняется единообразно.

    Дано существует пользователь с действующей сессией
    И access-токен корректно подписан и не истёк
    Когда клиент запрашивает профиль с вариантом авторизации <вид>
    Тогда запрос отклоняется как неудачная авторизация
    И ответ дословно совпадает с единым отказом авторизации
    И профиль пользователя не возвращается
    """

    @pytest.mark.parametrize("variant", AUTHORIZATION_VARIANTS)
    async def test_should_refuse_every_invalid_authorization_variant_identically(
        self, profile_auth_refusal_statements: ProfileAuthRefusalStatements, variant: str
    ):
        user = await profile_auth_refusal_statements.sign_in_user()

        refusal = await profile_auth_refusal_statements.request_profile_with_variant(variant, user)

        profile_auth_refusal_statements.assert_refused_with_unified_authorization_refusal(refusal)
        profile_auth_refusal_statements.assert_profile_is_not_returned(refusal, user)
