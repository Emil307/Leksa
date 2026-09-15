from dataclasses import dataclass
from typing import Any

from clients.application.auth_client import CHALLENGE_VERIFY_PATH, AuthClient
from clients.application.dto.auth.session_dto import SessionDto
from httpx import AsyncClient

from statements.auth_statements import HTTP_OK, AuthStatements, RequestedCode, is_canonical_uuid
from statements.environment import required_setting
from statements.outbox_database import OutboxDatabase

MAX_ATTEMPTS_VARIABLE = "AUTH_CHALLENGE_MAX_ATTEMPTS"
HTTP_UNAUTHORIZED = 401
UNAUTHORIZED_CODE = "UNAUTHORIZED"
ASCII_DIGITS = "0123456789"
SHIFTED_DIGITS = "1234567890"


def configured_max_attempts() -> int:
    return int(required_setting(MAX_ATTEMPTS_VARIABLE))


def _wrong_code_of(code: str) -> str:
    shifted = code.translate(str.maketrans(ASCII_DIGITS, SHIFTED_DIGITS))
    assert shifted != code, f"the wrong code must differ from the working code {code!r}"
    return shifted


@dataclass(frozen=True)
class RejectedVerification:
    http_status: int
    code: str | None
    body: dict[str, Any]


class LastAttemptSuccessStatements:
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

    async def given_user_holding_a_working_code(self) -> RequestedCode:
        email = self.auth_statements.new_user_email()
        return await self.auth_statements.request_code_and_capture(email)

    async def spend_every_attempt_but_the_last(self, working: RequestedCode) -> None:
        allowed = configured_max_attempts()
        wrong = _wrong_code_of(working.code)
        for spent in range(1, allowed):
            answer = await self.auth_client.verify_challenge(working.challenge_id, wrong)
            assert answer.http_status == HTTP_UNAUTHORIZED, (
                f"wrong-code attempt {spent} of {allowed} must be refused with {HTTP_UNAUTHORIZED}, "
                f"got {answer.http_status}"
            )
            assert answer.session_id is None, (
                f"wrong-code attempt {spent} of {allowed} must issue no session, got {answer.session_id!r}"
            )

    async def verify_the_correct_code(self, working: RequestedCode) -> SessionDto:
        return await self.auth_client.verify_challenge(working.challenge_id, working.code)

    def assert_session_was_issued(self, session: SessionDto) -> None:
        allowed = configured_max_attempts()
        assert session.http_status == HTTP_OK, (
            f"the correct code presented on attempt {allowed} of {allowed} — the last allowed one — "
            f"must be accepted with {HTTP_OK}, got {session.http_status}"
        )
        assert is_canonical_uuid(session.session_id), (
            f"the issued session must carry a canonical UUID id, got {session.session_id!r}"
        )
        assert is_canonical_uuid(session.user_id), (
            f"the issued session must name a canonical UUID user id, got {session.user_id!r}"
        )
        assert session.refresh_token, "the issued session must carry a refresh token"
        assert session.access_token, "the issued session must carry an access token"

    async def verify_the_same_code_again(self, working: RequestedCode) -> RejectedVerification:
        response = await self.http_client.post(
            CHALLENGE_VERIFY_PATH,
            json={"challengeId": working.challenge_id, "code": working.code},
        )
        body = response.json() if response.headers.get("content-type", "").startswith("application/json") else {}
        body = body if isinstance(body, dict) else {}
        return RejectedVerification(http_status=response.status_code, code=body.get("code"), body=body)

    def assert_rejected_as_failed_authorization(self, rejected: RejectedVerification) -> None:
        assert rejected.http_status == HTTP_UNAUTHORIZED, (
            f"replaying the spent code must be refused with {HTTP_UNAUTHORIZED}, got {rejected.http_status}"
        )
        assert rejected.code == UNAUTHORIZED_CODE, (
            f"the refusal must carry code {UNAUTHORIZED_CODE!r}, got {rejected.code!r} in {rejected.body!r}"
        )
