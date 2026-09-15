import pytest
from clients.application.profile_client import ProfileClient
from statements.auth_database import AuthDatabase
from statements.profile_field_fidelity_statements import ProfileFieldFidelityStatements

from tests.backend.abstract_backend_test import AbstractBackendTest


@pytest.fixture
def field_fidelity_statements(
    profile_client: ProfileClient, auth_database: AuthDatabase
) -> ProfileFieldFidelityStatements:
    return ProfileFieldFidelityStatements(profile_client, auth_database)


class TestProfileFieldFidelityAcceptance(AbstractBackendTest):
    """Сценарий 1.2: nullable-поля, Unicode и даты возвращаются без подмены.

    Дано пользователь имеет действующую сессию и корректный access-токен
    И nullable-поля его учётной записи не заполнены
    И текстовые поля содержат многобайтный текст, комбинируемые символы и метасимволы
    Когда пользователь запрашивает свой профиль
    Тогда запрос успешно выполнен
    И каждое незаполненное поле представлено как null
    И precomposed и combining-form текст возвращены byte-exact относительно хранения без нормализации на чтении
    И ответ остаётся валидным UTF-8 JSON
    И при враждебных locale и timezone моменты времени представлены в UTC, а день рождения — календарной датой
    """

    async def test_should_represent_every_unfilled_field_as_null(
        self, field_fidelity_statements: ProfileFieldFidelityStatements
    ):
        account = await field_fidelity_statements.sign_in_user_with_every_nullable_field_empty()

        response = await field_fidelity_statements.request_own_profile_from_hostile_locale_and_timezone(account)

        field_fidelity_statements.assert_request_succeeded(response)
        field_fidelity_statements.assert_every_unfilled_field_is_null(response)
        field_fidelity_statements.assert_body_is_valid_utf8_json(response)

    async def test_should_return_multibyte_and_combining_text_byte_exact(
        self, field_fidelity_statements: ProfileFieldFidelityStatements
    ):
        account = await field_fidelity_statements.sign_in_user_with_multibyte_combining_and_metacharacter_text()

        response = await field_fidelity_statements.request_own_profile_from_hostile_locale_and_timezone(account)

        field_fidelity_statements.assert_request_succeeded(response)
        field_fidelity_statements.assert_text_is_returned_byte_exact(response, account)
        field_fidelity_statements.assert_body_is_valid_utf8_json(response)

    async def test_should_render_instants_in_utc_and_birthday_as_a_calendar_date(
        self, field_fidelity_statements: ProfileFieldFidelityStatements
    ):
        account = await field_fidelity_statements.sign_in_user_with_day_edge_moments()

        response = await field_fidelity_statements.request_own_profile_from_hostile_locale_and_timezone(account)

        field_fidelity_statements.assert_request_succeeded(response)
        field_fidelity_statements.assert_instants_are_in_utc(response, account)
        field_fidelity_statements.assert_birthday_is_a_calendar_date(response, account)
        field_fidelity_statements.assert_body_is_valid_utf8_json(response)
