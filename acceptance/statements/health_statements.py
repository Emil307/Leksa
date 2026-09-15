from clients.application.health_client import HealthClient

UP = "UP"


class HealthStatements:
    def __init__(self, health_client: HealthClient):
        self.health_client = health_client

    async def assert_application_reports_healthy(self) -> None:
        health = await self.health_client.fetch()

        assert health.http_status == 200
        assert health.status == UP
        assert health.database == UP
