import pytest
from clients.application.profile_client import ProfileClient
from statements.auth_database import AuthDatabase
from statements.profile_serialization_statements import ProfileSerializationStatements

from tests.backend.abstract_backend_test import AbstractBackendTest


@pytest.fixture
def profile_serialization_statements(
    profile_client: ProfileClient, auth_database: AuthDatabase
) -> ProfileSerializationStatements:
    return ProfileSerializationStatements(profile_client, auth_database)


class TestProfileSerializationAcceptance(AbstractBackendTest):
    """Сценарий 3.1: профиль возвращает безопасно сериализованные данные владельца токена.

    Дано два пользователя имеют разные учётные записи и действующие сессии
    И текстовые поля учётной записи первого пользователя содержат HTML, SQL, перевод строки
    и управляющие метасимволы
    И первый пользователь предъявляет свой корректный access-токен
    Когда первый пользователь запрашивает профиль с чужим существующим и несуществующим
    идентификаторами
    Тогда оба ответа дословно совпадают
    И оба ответа содержат только учётную запись первого пользователя
    И существование и данные второго пользователя не раскрываются
    И каждый ответ остаётся одним валидным JSON-документом
    И каждое опасное значение возвращено как строковые данные
    И значение не создаёт новый заголовок, поле JSON, запрос или строку лога
    """

    async def test_should_ignore_foreign_identifiers_and_return_hostile_text_as_data(
        self, profile_serialization_statements: ProfileSerializationStatements
    ):
        statements = profile_serialization_statements
        accounts = await statements.sign_in_two_users_with_hostile_text_in_the_first_account()

        existing = await statements.request_profile_for_existing_foreign_identifier(accounts)
        unknown = await statements.request_profile_for_unknown_identifier(accounts)

        statements.assert_both_responses_are_verbatim_equal(existing, unknown)
        statements.assert_each_response_is_the_owners_safe_document((existing, unknown), accounts)
