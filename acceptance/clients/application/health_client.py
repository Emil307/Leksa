from clients.application.application_client import ApplicationClient
from clients.application.dto.health.health_dto import HealthDto

HEALTH_PATH = "/health"


class HealthClient(ApplicationClient):
    async def fetch(self) -> HealthDto:
        response = await self.get(HEALTH_PATH)
        body = response.json()
        return HealthDto(
            http_status=response.status_code,
            status=body["status"],
            database=body["database"],
        )
