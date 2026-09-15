from dataclasses import dataclass
from typing import Any

from clients.application.auth_client import CHALLENGE_START_PATH, AuthClient

from statements.auth_statements import HTTP_OK, AuthStatements
from statements.outbox_database import OutboxDatabase

HTTP_BAD_REQUEST = 400
VALIDATION_FAILED = "VALIDATION_FAILED"
EMAIL_FIELD = "email"
CHALLENGE_TYPE_FIELD = "challengeType"
UNREGISTERED_CHALLENGE_TYPE = "TELEGRAM_CODE"
LOWERCASE_REGISTERED_CHALLENGE_TYPE = "email_code"
CHALLENGE_FIELDS = frozenset({"challengeId", "challengeType", "expiresAt"})


@dataclass(frozen=True)
class RejectedStrategylessStart:
    http_status: int
    error_code: str | None
    response_field_names: frozenset[str]
    offered_email: str
    offered_type: str


class UnregisteredChallengeStrategyStatements:
    def __init__(
        self,
        auth_client: AuthClient,
        auth_statements: AuthStatements,
        outbox_database: OutboxDatabase,
    ):
        self.auth_client = auth_client
        self.auth_statements = auth_statements
        self.outbox_database = outbox_database

    async def request_code_with_a_type_without_a_strategy(self) -> RejectedStrategylessStart:
        return await self._start(UNREGISTERED_CHALLENGE_TYPE)

    async def request_code_with_a_lowercase_registered_type(self) -> RejectedStrategylessStart:
        return await self._start(LOWERCASE_REGISTERED_CHALLENGE_TYPE)

    def assert_rejected_with_an_explicit_error(self, rejection: RejectedStrategylessStart) -> None:
        assert rejection.http_status == HTTP_BAD_REQUEST, (
            f"challenge type {rejection.offered_type!r} has no registered strategy and must be rejected "
            f"with {HTTP_BAD_REQUEST}, got {rejection.http_status}"
        )
        assert rejection.error_code == VALIDATION_FAILED, (
            f"challenge type {rejection.offered_type!r} must be rejected with code {VALIDATION_FAILED!r}, "
            f"got {rejection.error_code!r}"
        )

    async def assert_no_request_was_queued(self, rejection: RejectedStrategylessStart) -> None:
        queued = await self.outbox_database.queued_code_for(rejection.offered_email)
        assert queued is None, (
            f"challenge type {rejection.offered_type!r} must queue nothing for {rejection.offered_email!r}, "
            f"found code {queued!r}"
        )

    def assert_no_challenge_was_handed_out(self, rejection: RejectedStrategylessStart) -> None:
        leaked = rejection.response_field_names & CHALLENGE_FIELDS
        assert leaked == frozenset(), (
            f"challenge type {rejection.offered_type!r} must not fall back to the default strategy — "
            f"the rejection must carry none of {sorted(CHALLENGE_FIELDS)}, got {sorted(leaked)}"
        )

    async def assert_the_address_stayed_free_for_a_registered_type(self, rejection: RejectedStrategylessStart) -> None:
        retry = await self.auth_statements.request_code(rejection.offered_email)
        assert retry.http_status == HTTP_OK, (
            f"challenge type {rejection.offered_type!r} must leave no challenge and no cooldown for "
            f"{rejection.offered_email!r} — the next registered-type request must be accepted with {HTTP_OK}, "
            f"got {retry.http_status}"
        )

    async def _start(self, challenge_type: str) -> RejectedStrategylessStart:
        offered_email = self.auth_statements.new_user_email()
        body = {EMAIL_FIELD: offered_email, CHALLENGE_TYPE_FIELD: challenge_type}
        response = await self.auth_client.post(CHALLENGE_START_PATH, json=body)
        payload = self._payload(response.json())
        return RejectedStrategylessStart(
            http_status=response.status_code,
            error_code=payload.get("code"),
            response_field_names=frozenset(payload),
            offered_email=offered_email,
            offered_type=challenge_type,
        )

    @staticmethod
    def _payload(body: Any) -> dict[str, Any]:
        return body if isinstance(body, dict) else {}
