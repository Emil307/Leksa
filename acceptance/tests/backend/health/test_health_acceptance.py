from statements.health_statements import HealthStatements

from tests.backend.abstract_backend_test import AbstractBackendTest


class TestHealthAcceptance(AbstractBackendTest):
    """Scenario: the running application reports itself healthy.

    Given the stack is running with its database
    When a client requests the health endpoint
    Then the application answers 200 with status UP and an available database
    """

    async def test_should_report_the_running_application_as_healthy(self, health_statements: HealthStatements):
        await health_statements.assert_application_reports_healthy()
