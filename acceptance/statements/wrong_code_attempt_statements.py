from dataclasses import dataclass
from typing import Any

from clients.application.auth_client import AuthClient
from clients.application.dto.auth.session_dto import SessionDto
from httpx import Response

from statements.auth_statements import AuthStatements, RequestedCode, is_canonical_uuid
from statements.outbox_database import OutboxDatabase

VERIFY_PATH = "/api/v1/auth/challenge/verify"
HTTP_UNAUTHORIZED = 401
UNAUTHORIZED = "UNAUTHORIZED"
ERROR_ENVELOPE_FIELDS = frozenset({"code", "message", "payload"})
SESSION_BEARING_NAMES = ("session", "user", "accessToken", "refreshToken", "token")
ATTEMPT_BEARING_NAMES = ("attempt", "Attempt", "remaining", "Remaining", "left", "попыт", "остат")
DIGIT_SHIFT = 1
DECIMAL_BASE = 10


@dataclass(frozen=True)
class RejectedVerify:
    http_status: int
    body: dict[str, Any]


def _shifted(code: str) -> str:
    return "".join(str((int(digit) + DIGIT_SHIFT) % DECIMAL_BASE) for digit in code)


class WrongCodeAttemptStatements:
    def __init__(
        self,
        auth_client: AuthClient,
        auth_statements: AuthStatements,
        outbox_database: OutboxDatabase,
    ):
        self.auth_client = auth_client
        self.auth_statements = auth_statements
        self.outbox_database = outbox_database

    async def given_user_holding_a_working_code(self) -> RequestedCode:
        email = self.auth_statements.new_user_email()
        return await self.auth_statements.request_code_and_capture(email)

    def wrong_code_for(self, working: RequestedCode) -> str:
        wrong = _shifted(working.code)
        assert wrong != working.code and len(wrong) == len(working.code) and wrong.isdigit(), (
            f"the wrong code must stay a same-length digit string differing from {working.code!r}, got {wrong!r}"
        )
        return wrong

    async def verify_with(self, working: RequestedCode, code: str) -> RejectedVerify:
        response = await self.auth_client.post(VERIFY_PATH, json={"challengeId": working.challenge_id, "code": code})
        return RejectedVerify(response.status_code, self._body_of(response))

    def assert_rejected_as_failed_authorization(self, rejected: RejectedVerify) -> None:
        assert rejected.http_status == HTTP_UNAUTHORIZED, (
            f"a wrong code must be refused as failed authorization with {HTTP_UNAUTHORIZED}, "
            f"got {rejected.http_status} with body {rejected.body!r}"
        )
        assert rejected.body.get("code") == UNAUTHORIZED, (
            f"a wrong code must answer error code {UNAUTHORIZED}, got {rejected.body.get('code')!r}"
        )
        assert frozenset(rejected.body) == ERROR_ENVELOPE_FIELDS, (
            f"a wrong code must answer exactly {sorted(ERROR_ENVELOPE_FIELDS)}, got {sorted(rejected.body)}"
        )
        assert rejected.body.get("message"), (
            f"a wrong code must carry its own message, got {rejected.body.get('message')!r}"
        )

    def assert_carries_no_attempt_remainder_no_session_and_no_token(self, rejected: RejectedVerify) -> None:
        rendered = repr(rejected.body)
        leaked_attempts = [name for name in ATTEMPT_BEARING_NAMES if name in rendered]
        assert not leaked_attempts, (
            f"a wrong code must never disclose the attempt remainder, found {leaked_attempts!r} in {rejected.body!r}"
        )
        leaked_session = [name for name in SESSION_BEARING_NAMES if name in rendered]
        assert not leaked_session, (
            f"a wrong code must carry neither a session nor a token, found {leaked_session!r} in {rejected.body!r}"
        )

    async def assert_the_valid_code_still_issues_a_session(self, working: RequestedCode) -> None:
        session = await self.auth_client.verify_challenge(working.challenge_id, working.code)
        self.auth_statements.assert_verify_accepted(session)
        self._assert_session_is_complete(session)

    def _assert_session_is_complete(self, session: SessionDto) -> None:
        assert is_canonical_uuid(session.user_id), (
            f"the valid code must still answer with a canonical user id, got {session.user_id!r}"
        )
        assert is_canonical_uuid(session.session_id), (
            f"the valid code must still answer with a canonical session id, got {session.session_id!r}"
        )
        assert session.refresh_token, "the valid code must still answer with a refresh token"
        assert session.access_token, "the valid code must still answer with an access token"

    @staticmethod
    def _body_of(response: Response) -> dict[str, Any]:
        try:
            body = response.json()
        except ValueError:
            return {}
        return body if isinstance(body, dict) else {}
