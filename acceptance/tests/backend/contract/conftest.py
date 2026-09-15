import pytest
from clients.application.contract_client import ContractClient
from httpx import AsyncClient
from statements.api_contract_statements import ApiContractStatements


@pytest.fixture
def contract_client(http_client: AsyncClient) -> ContractClient:
    return ContractClient(http_client)


@pytest.fixture
def api_contract_statements(contract_client: ContractClient) -> ApiContractStatements:
    return ApiContractStatements(contract_client)
