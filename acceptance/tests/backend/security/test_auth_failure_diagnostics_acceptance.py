import pytest
from clients.application.profile_client import ProfileClient
from statements.auth_database import AuthDatabase
from statements.auth_failure_diagnostics_statements import AuthFailureDiagnosticsStatements

from tests.backend.abstract_backend_test import AbstractBackendTest


@pytest.fixture
def auth_failure_statements(
    profile_client: ProfileClient, auth_database: AuthDatabase
) -> AuthFailureDiagnosticsStatements:
    return AuthFailureDiagnosticsStatements(profile_client, auth_database)


class TestAuthFailureDiagnosticsAcceptance(AbstractBackendTest):
    """Сценарий 4.1: каждый auth-отказ диагностируется безопасно и закрывает доступ к профилю.

    Дано токен, refresh-токен, секрет подписи и персональные данные имеют узнаваемые метки
    с переводом строки и управляющими символами
    И пользователь имеет действующую сессию и корректный access-токен
    Когда возникает auth-отказ вида <вид>
    Тогда клиент получает дословно единый отказ авторизации
    И ответ содержит фиксированную метку редактирования вместо секретов и персональных данных
    И ответ не содержит внутренних деталей приложения
    И запрос отклоняется как неудачная авторизация
    И профиль не возвращается
    """

    async def test_should_refuse_safely_when_header_is_not_parsable(
        self, auth_failure_statements: AuthFailureDiagnosticsStatements
    ):
        user = await auth_failure_statements.sign_in_user_with_marked_personal_data()

        attempt = await auth_failure_statements.request_profile_with_unparsable_header()

        auth_failure_statements.assert_refusal_is_safe(attempt, user)

    async def test_should_refuse_safely_when_signature_does_not_verify(
        self, auth_failure_statements: AuthFailureDiagnosticsStatements
    ):
        user = await auth_failure_statements.sign_in_user_with_marked_personal_data()

        attempt = await auth_failure_statements.request_profile_with_tampered_signature(user)

        auth_failure_statements.assert_refusal_is_safe(attempt, user)

    async def test_should_refuse_safely_when_claims_do_not_pass_validation(
        self, auth_failure_statements: AuthFailureDiagnosticsStatements
    ):
        user = await auth_failure_statements.sign_in_user_with_marked_personal_data()

        attempt = await auth_failure_statements.request_profile_with_foreign_audience(user)

        auth_failure_statements.assert_refusal_is_safe(attempt, user)

    async def test_should_refuse_safely_when_session_has_expired(
        self, auth_failure_statements: AuthFailureDiagnosticsStatements
    ):
        user = await auth_failure_statements.sign_in_user_whose_session_has_expired()

        attempt = await auth_failure_statements.request_profile_with_valid_token(user)

        auth_failure_statements.assert_refusal_is_safe(attempt, user)

    async def test_should_refuse_safely_when_account_is_absent_after_session_check(
        self, auth_failure_statements: AuthFailureDiagnosticsStatements
    ):
        user = await auth_failure_statements.sign_in_user_whose_account_is_absent()

        attempt = await auth_failure_statements.request_profile_with_valid_token(user)

        auth_failure_statements.assert_refusal_is_safe(attempt, user)
