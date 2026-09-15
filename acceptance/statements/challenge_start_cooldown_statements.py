from dataclasses import dataclass
from typing import Any

import asyncpg
from clients.application.auth_client import CHALLENGE_START_PATH, AuthClient
from clients.application.dto.auth.session_dto import SessionDto
from httpx import AsyncClient

from statements.auth_database import connection_settings
from statements.auth_statements import EMAIL_CODE, AuthStatements, RequestedCode
from statements.outbox_database import OutboxDatabase

HTTP_CONFLICT = 409
CONFLICT_CODE = "CONFLICT"
RETRY_AFTER_KEY = "retryAfterSeconds"
SINGLE_QUEUED_REQUEST = 1

COUNT_QUEUED_EMAILS = """
SELECT count(*) FROM notifications.t_outbox WHERE type = 'EMAIL' AND data->>'to' = $1
"""


@dataclass(frozen=True)
class CooldownDenial:
    http_status: int
    code: str | None
    payload: dict[str, Any]


class ChallengeStartCooldownStatements:
    def __init__(
        self,
        http_client: AsyncClient,
        auth_client: AuthClient,
        auth_statements: AuthStatements,
        outbox_database: OutboxDatabase,
    ):
        self.http_client = http_client
        self.auth_client = auth_client
        self.auth_statements = auth_statements
        self.outbox_database = outbox_database

    async def given_user_just_requested_a_code(self) -> tuple[str, RequestedCode]:
        email = self.auth_statements.new_user_email()
        requested = await self.auth_statements.request_code_and_capture(email)
        await self.assert_single_queued_request(email)
        return email, requested

    async def request_code_again(self, email: str) -> CooldownDenial:
        response = await self.http_client.post(CHALLENGE_START_PATH, json={"email": email, "challengeType": EMAIL_CODE})
        body = response.json() if response.content else {}
        body = body if isinstance(body, dict) else {}
        payload = body.get("payload")
        return CooldownDenial(
            http_status=response.status_code,
            code=body.get("code"),
            payload=payload if isinstance(payload, dict) else {},
        )

    def assert_rejected_by_cooldown(self, denial: CooldownDenial) -> None:
        assert denial.http_status == HTTP_CONFLICT, (
            f"a repeat code request inside the cooldown must be rejected with {HTTP_CONFLICT}, got {denial.http_status}"
        )
        assert denial.code == CONFLICT_CODE, f"the refusal must carry code {CONFLICT_CODE!r}, got {denial.code!r}"

    def assert_carries_remaining_wait_in_whole_seconds(self, denial: CooldownDenial) -> None:
        assert RETRY_AFTER_KEY in denial.payload, (
            f"the refusal payload must carry {RETRY_AFTER_KEY!r}, got {sorted(denial.payload)}"
        )
        remaining = denial.payload[RETRY_AFTER_KEY]
        assert isinstance(remaining, int) and not isinstance(remaining, bool), (
            f"{RETRY_AFTER_KEY} must be whole seconds as an integer, got {remaining!r}"
        )
        assert remaining >= 1, f"{RETRY_AFTER_KEY} must be at least 1 second while the cooldown holds, got {remaining}"

    def assert_remaining_wait_does_not_grow(self, earlier: CooldownDenial, later: CooldownDenial) -> None:
        first = earlier.payload[RETRY_AFTER_KEY]
        second = later.payload[RETRY_AFTER_KEY]
        assert second <= first, (
            f"{RETRY_AFTER_KEY} must count down, not grow — the later refusal reported {second} after {first}"
        )

    async def assert_single_queued_request(self, email: str) -> None:
        queued = await self._count_queued_emails(email)
        assert queued == SINGLE_QUEUED_REQUEST, (
            f"{email} must keep exactly {SINGLE_QUEUED_REQUEST} queued email request, found {queued}"
        )

    async def assert_earlier_code_still_issues_a_session(self, requested: RequestedCode) -> SessionDto:
        session = await self.auth_client.verify_challenge(requested.challenge_id, requested.code)
        self.auth_statements.assert_verify_accepted(session)
        assert session.session_id, "the earlier code must still issue a session carrying an id"
        assert session.refresh_token, "the earlier code must still issue a session carrying a refresh token"
        assert session.access_token, "the earlier code must still issue a session carrying an access token"
        return session

    async def _count_queued_emails(self, email: str) -> int:
        connection = await asyncpg.connect(**connection_settings())
        try:
            return await connection.fetchval(COUNT_QUEUED_EMAILS, email)
        finally:
            await connection.close()
