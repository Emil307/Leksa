from clients.application.application_client import ApplicationClient
from clients.application.dto.contract.api_contract_dto import ApiContractDto

CONTRACT_PATH = "/openapi.json"

COMPONENTS_KEY = "components"
SECURITY_SCHEMES_KEY = "securitySchemes"
PATHS_KEY = "paths"


class ContractClient(ApplicationClient):
    async def fetch_published_contract(self) -> ApiContractDto:
        response = await self.get(CONTRACT_PATH)

        body = self._json_object(response)
        components = self._nested_object(body, COMPONENTS_KEY)
        return ApiContractDto(
            http_status=response.status_code,
            security_schemes=self._nested_object(components, SECURITY_SCHEMES_KEY),
            paths=self._nested_object(body, PATHS_KEY),
        )
