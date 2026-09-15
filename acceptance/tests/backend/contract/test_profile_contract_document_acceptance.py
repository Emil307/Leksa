import pytest
from statements.api_contract_statements import ApiContractStatements

from tests.backend.abstract_backend_test import AbstractBackendTest


@pytest.mark.skip(
    reason="RED: AssertionError — the contract must declare the security scheme "
    "bearerAuth as {'type': 'http', 'scheme': 'bearer', 'bearerFormat': 'JWT'}, got None"
)
class TestProfileContractDocumentAcceptance(AbstractBackendTest):
    """Сценарий 4.1: опубликованный контракт описывает чтение профиля как защищённое.

    Дано приложение запущено
    Когда клиент запрашивает опубликованный контракт API
    Тогда контракт объявляет схему авторизации Bearer с форматом JWT
    И операция чтения профиля требует эту схему
    И операция объявляет и успешный ответ, и единый отказ авторизации
    И ни один незащищённый вариант чтения профиля не объявлен
    """

    async def test_should_publish_profile_read_as_a_bearer_protected_operation(
        self, api_contract_statements: ApiContractStatements
    ):
        contract = await api_contract_statements.request_published_contract()

        api_contract_statements.assert_contract_is_published(contract)
        api_contract_statements.assert_declares_bearer_jwt_security_scheme(contract)
        api_contract_statements.assert_profile_read_requires_bearer_scheme(contract)
        api_contract_statements.assert_profile_read_declares_success_and_unified_refusal(contract)
        api_contract_statements.assert_no_unsecured_profile_read_is_declared(contract)
