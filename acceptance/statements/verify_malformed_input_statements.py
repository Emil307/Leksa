from dataclasses import dataclass
from typing import Any

from clients.application.auth_client import AuthClient
from clients.application.dto.auth.session_dto import SessionDto
from httpx import Response

from statements.auth_statements import AuthStatements, RequestedCode, is_canonical_uuid
from statements.outbox_database import OutboxDatabase

VERIFY_PATH = "/api/v1/auth/challenge/verify"
HTTP_BAD_REQUEST = 400
VALIDATION_FAILED = "VALIDATION_FAILED"
ERROR_ENVELOPE_FIELDS = frozenset({"code", "message", "payload"})
SESSION_BEARING_NAMES = ("session", "user", "accessToken", "refreshToken", "token")
ASCII_DIGITS = "0123456789"
ARABIC_INDIC_DIGITS = "٠١٢٣٤٥٦٧٨٩"
FULLWIDTH_DIGITS = "０１２３４５６７８９"
LETTER_INSTEAD_OF_DIGIT = "a"


@dataclass(frozen=True)
class MalformedAttempt:
    label: str
    payload: dict[str, Any]


@dataclass(frozen=True)
class RejectedAttempt:
    label: str
    http_status: int
    body: dict[str, Any]


def _transliterated(code: str, digits: str) -> str:
    return code.translate(str.maketrans(ASCII_DIGITS, digits))


class VerifyMalformedInputStatements:
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

    def malformed_challenge_identifiers(self, working: RequestedCode) -> list[MalformedAttempt]:
        code = working.code
        return [
            MalformedAttempt("challengeId отсутствует в теле", {"code": code}),
            MalformedAttempt("challengeId равен null", {"challengeId": None, "code": code}),
            MalformedAttempt("challengeId не UUID", {"challengeId": "not-a-uuid", "code": code}),
            MalformedAttempt("challengeId число, а не строка", {"challengeId": 12345, "code": code}),
        ]

    def malformed_codes(self, working: RequestedCode) -> list[MalformedAttempt]:
        challenge_id = working.challenge_id
        code = working.code
        return [
            MalformedAttempt("код отсутствует в теле", {"challengeId": challenge_id}),
            MalformedAttempt("код равен null", {"challengeId": challenge_id, "code": None}),
            MalformedAttempt("код — пустая строка", {"challengeId": challenge_id, "code": ""}),
            MalformedAttempt("код из пяти цифр", {"challengeId": challenge_id, "code": code[:-1]}),
            MalformedAttempt("код из семи цифр", {"challengeId": challenge_id, "code": code + code[-1]}),
            MalformedAttempt(
                "код из шести символов, один из которых буква",
                {"challengeId": challenge_id, "code": code[:-1] + LETTER_INSTEAD_OF_DIGIT},
            ),
            MalformedAttempt(
                "код — число JSON, а не строка (ведущий ноль потерян)",
                {"challengeId": challenge_id, "code": int(code)},
            ),
            MalformedAttempt(
                "код из арабо-индийских цифр, численно равный верному",
                {"challengeId": challenge_id, "code": _transliterated(code, ARABIC_INDIC_DIGITS)},
            ),
            MalformedAttempt(
                "код из полноширинных цифр, численно равный верному",
                {"challengeId": challenge_id, "code": _transliterated(code, FULLWIDTH_DIGITS)},
            ),
        ]

    async def send_each_and_assert_rejected_as_invalid_input(self, attempts: list[MalformedAttempt]) -> None:
        for attempt in attempts:
            rejected = await self._send(attempt)
            self._assert_rejected_as_invalid_input(rejected)
            self._assert_carries_neither_session_nor_token(rejected)

    async def assert_attempts_untouched_and_valid_code_still_issues_a_session(self, working: RequestedCode) -> None:
        session = await self.auth_client.verify_challenge(working.challenge_id, working.code)
        self.auth_statements.assert_verify_accepted(session)
        self._assert_session_is_complete(session)

    async def _send(self, attempt: MalformedAttempt) -> RejectedAttempt:
        response = await self.auth_client.post(VERIFY_PATH, json=attempt.payload)
        return RejectedAttempt(attempt.label, response.status_code, self._body_of(response))

    def _assert_rejected_as_invalid_input(self, rejected: RejectedAttempt) -> None:
        assert rejected.http_status == HTTP_BAD_REQUEST, (
            f"«{rejected.label}» must be refused as invalid input with {HTTP_BAD_REQUEST}, "
            f"got {rejected.http_status} with body {rejected.body!r}"
        )
        assert rejected.body.get("code") == VALIDATION_FAILED, (
            f"«{rejected.label}» must answer error code {VALIDATION_FAILED}, got {rejected.body.get('code')!r}"
        )
        assert frozenset(rejected.body) == ERROR_ENVELOPE_FIELDS, (
            f"«{rejected.label}» must answer exactly {sorted(ERROR_ENVELOPE_FIELDS)}, got {sorted(rejected.body)}"
        )

    def _assert_carries_neither_session_nor_token(self, rejected: RejectedAttempt) -> None:
        rendered = repr(rejected.body)
        leaked = [name for name in SESSION_BEARING_NAMES if name in rendered]
        assert not leaked, (
            f"«{rejected.label}» must carry neither a session nor a token, found {leaked!r} in {rejected.body!r}"
        )

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
