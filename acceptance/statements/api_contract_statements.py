from typing import Any

from clients.application.contract_client import ContractClient
from clients.application.dto.contract.api_contract_dto import ApiContractDto

from statements.wire_contract import HTTP_OK

PROFILE_READ_PATH = "/api/v1/profile"
READ_METHOD = "get"
PROFILE_PATH_MARKER = "profile"

BEARER_SCHEME_NAME = "bearerAuth"
BEARER_SCHEME_DEFINITION = {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}

SECURITY_KEY = "security"
RESPONSES_KEY = "responses"
DECLARED_RESPONSE_CODES = frozenset({"200", "401"})


class ApiContractStatements:
    def __init__(self, contract_client: ContractClient):
        self.contract_client = contract_client

    async def request_published_contract(self) -> ApiContractDto:
        return await self.contract_client.fetch_published_contract()

    def assert_contract_is_published(self, contract: ApiContractDto) -> None:
        assert contract.http_status == HTTP_OK, (
            f"the running application must publish its API contract with {HTTP_OK}, got {contract.http_status}"
        )

    def assert_declares_bearer_jwt_security_scheme(self, contract: ApiContractDto) -> None:
        scheme = contract.security_schemes.get(BEARER_SCHEME_NAME)

        assert scheme == BEARER_SCHEME_DEFINITION, (
            f"the contract must declare the security scheme {BEARER_SCHEME_NAME} as "
            f"{BEARER_SCHEME_DEFINITION}, got {scheme}"
        )

    def assert_profile_read_requires_bearer_scheme(self, contract: ApiContractDto) -> None:
        operation = self._profile_read_operation(contract)
        requirements = self._security_requirements(operation)

        assert self._requires_bearer_scheme(operation), (
            f"the profile read operation must require {BEARER_SCHEME_NAME}, got security {requirements}"
        )

    def assert_profile_read_declares_success_and_unified_refusal(self, contract: ApiContractDto) -> None:
        operation = self._profile_read_operation(contract)
        responses = operation.get(RESPONSES_KEY)
        declared = frozenset(responses) if isinstance(responses, dict) else frozenset()

        assert declared == DECLARED_RESPONSE_CODES, (
            f"the profile read operation must declare exactly {sorted(DECLARED_RESPONSE_CODES)} responses, "
            f"got {sorted(declared)}"
        )

    def assert_no_unsecured_profile_read_is_declared(self, contract: ApiContractDto) -> None:
        unsecured = [
            f"{method.upper()} {path}"
            for path, operations in contract.paths.items()
            if PROFILE_PATH_MARKER in path and isinstance(operations, dict)
            for method, operation in operations.items()
            if isinstance(operation, dict) and not self._requires_bearer_scheme(operation)
        ]

        assert unsecured == [], f"no profile read may be published without {BEARER_SCHEME_NAME}, found {unsecured}"

    @classmethod
    def _requires_bearer_scheme(cls, operation: dict[str, Any]) -> bool:
        return any(BEARER_SCHEME_NAME in requirement for requirement in cls._security_requirements(operation))

    @staticmethod
    def _profile_read_operation(contract: ApiContractDto) -> dict[str, Any]:
        operations = contract.paths.get(PROFILE_READ_PATH)
        assert isinstance(operations, dict), (
            f"the contract must publish the profile read path {PROFILE_READ_PATH}, got paths {sorted(contract.paths)}"
        )

        operation = operations.get(READ_METHOD)
        assert isinstance(operation, dict), (
            f"the contract must publish {READ_METHOD.upper()} {PROFILE_READ_PATH}, got {sorted(operations)}"
        )
        return operation

    @staticmethod
    def _security_requirements(operation: dict[str, Any]) -> list[Any]:
        requirements = operation.get(SECURITY_KEY)
        return requirements if isinstance(requirements, list) else []
