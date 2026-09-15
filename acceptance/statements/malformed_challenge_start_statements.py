from dataclasses import dataclass
from typing import Any

from clients.application.auth_client import CHALLENGE_START_PATH, AuthClient

from statements.auth_statements import HTTP_OK, AuthStatements
from statements.outbox_database import OutboxDatabase

HTTP_BAD_REQUEST = 400
VALIDATION_FAILED = "VALIDATION_FAILED"
EMAIL_FIELD = "email"
CHALLENGE_TYPE_FIELD = "challengeType"
EMAIL_CODE = "EMAIL_CODE"
UNKNOWN_CHALLENGE_TYPE = "SMS_CODE"
EMPTY = ""
NO_ADDRESS = ""


@dataclass(frozen=True)
class RejectedStart:
    http_status: int
    error_code: str | None
    offered_email: str


class MalformedChallengeStartStatements:
    def __init__(
        self,
        auth_client: AuthClient,
        auth_statements: AuthStatements,
        outbox_database: OutboxDatabase,
    ):
        self.auth_client = auth_client
        self.auth_statements = auth_statements
        self.outbox_database = outbox_database

    async def request_code_without_the_email_field(self) -> RejectedStart:
        return await self._start({CHALLENGE_TYPE_FIELD: EMAIL_CODE}, NO_ADDRESS)

    async def request_code_with_a_null_email(self) -> RejectedStart:
        return await self._start({EMAIL_FIELD: None, CHALLENGE_TYPE_FIELD: EMAIL_CODE}, NO_ADDRESS)

    async def request_code_with_an_empty_email(self) -> RejectedStart:
        return await self._start({EMAIL_FIELD: EMPTY, CHALLENGE_TYPE_FIELD: EMAIL_CODE}, EMPTY)

    async def request_code_with_an_email_without_an_at_sign(self) -> RejectedStart:
        offered = self.auth_statements.new_user_email().replace("@", ".")
        return await self._start({EMAIL_FIELD: offered, CHALLENGE_TYPE_FIELD: EMAIL_CODE}, offered)

    async def request_code_with_an_email_without_a_domain_part(self) -> RejectedStart:
        offered = self.auth_statements.new_user_email().split("@")[0] + "@"
        return await self._start({EMAIL_FIELD: offered, CHALLENGE_TYPE_FIELD: EMAIL_CODE}, offered)

    async def request_code_without_the_challenge_type_field(self) -> RejectedStart:
        offered = self.auth_statements.new_user_email()
        return await self._start({EMAIL_FIELD: offered}, offered)

    async def request_code_with_a_null_challenge_type(self) -> RejectedStart:
        offered = self.auth_statements.new_user_email()
        return await self._start({EMAIL_FIELD: offered, CHALLENGE_TYPE_FIELD: None}, offered)

    async def request_code_with_an_empty_challenge_type(self) -> RejectedStart:
        offered = self.auth_statements.new_user_email()
        return await self._start({EMAIL_FIELD: offered, CHALLENGE_TYPE_FIELD: EMPTY}, offered)

    async def request_code_with_an_unknown_challenge_type(self) -> RejectedStart:
        offered = self.auth_statements.new_user_email()
        return await self._start({EMAIL_FIELD: offered, CHALLENGE_TYPE_FIELD: UNKNOWN_CHALLENGE_TYPE}, offered)

    def assert_rejected_as_invalid_data(self, rejection: RejectedStart) -> None:
        assert rejection.http_status == HTTP_BAD_REQUEST, (
            f"a malformed code request must be rejected with {HTTP_BAD_REQUEST}, got {rejection.http_status}"
        )
        assert rejection.error_code == VALIDATION_FAILED, (
            f"a malformed code request must answer code {VALIDATION_FAILED!r}, got {rejection.error_code!r}"
        )

    async def assert_no_request_was_queued(self, rejection: RejectedStart) -> None:
        queued = await self.outbox_database.queued_code_for(rejection.offered_email)
        assert queued is None, (
            f"a rejected code request must queue nothing for {rejection.offered_email!r}, found code {queued!r}"
        )

    async def assert_no_live_challenge_holds_the_offered_email(self, rejection: RejectedStart) -> None:
        retry = await self.auth_statements.request_code(rejection.offered_email)
        assert retry.http_status == HTTP_OK, (
            f"a rejected code request must leave no live challenge for {rejection.offered_email!r} — "
            f"the next valid request must be accepted with {HTTP_OK}, got {retry.http_status}"
        )

    async def _start(self, body: dict[str, Any], offered_email: str) -> RejectedStart:
        response = await self.auth_client.post(CHALLENGE_START_PATH, json=body)
        return RejectedStart(
            http_status=response.status_code,
            error_code=self._error_code(response.json()),
            offered_email=offered_email,
        )

    @staticmethod
    def _error_code(body: Any) -> str | None:
        return body.get("code") if isinstance(body, dict) else None
