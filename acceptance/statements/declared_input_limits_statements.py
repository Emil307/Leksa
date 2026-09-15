import uuid
from dataclasses import dataclass
from typing import Any

from clients.application.auth_client import CHALLENGE_START_PATH, CHALLENGE_VERIFY_PATH, AuthClient
from httpx import Response

from statements.auth_statements import AuthStatements
from statements.outbox_database import OutboxDatabase

HTTP_BAD_REQUEST = 400
VALIDATION_FAILED = "VALIDATION_FAILED"
ERROR_ENVELOPE_FIELDS = frozenset({"code", "message", "payload"})
EMAIL_CODE = "EMAIL_CODE"
EMAIL_FIELD = "email"
CHALLENGE_TYPE_FIELD = "challengeType"
CHALLENGE_ID_FIELD = "challengeId"
CODE_FIELD = "code"
DECLARED_EMAIL_OCTETS = 254
OVERSIZED_EMAIL_OCTETS = 255
MEGABYTE = 1024 * 1024
OVERSIZED_BODY_MEGABYTES = 3
DOMAIN_PART = "@example.com"
ASCII_FILLER = "a"
TWO_OCTET_FILLER = "ы"
DIGIT_FILLER = "1"
SEVEN_DIGIT_CODE = "1234567"
SESSION_BEARING_NAMES = ("session", "user", "accessToken", "refreshToken")
NO_ADDRESS = ""


def _ascii_email_of_octets(octets: int) -> str:
    return ASCII_FILLER * (octets - len(DOMAIN_PART)) + DOMAIN_PART


def _multibyte_email_inside_the_character_limit() -> str:
    return TWO_OCTET_FILLER * (DECLARED_EMAIL_OCTETS - len(DOMAIN_PART)) + DOMAIN_PART


def _several_megabytes_of(filler: str) -> str:
    return filler * (OVERSIZED_BODY_MEGABYTES * MEGABYTE)


@dataclass(frozen=True)
class Rejection:
    label: str
    http_status: int
    body: dict[str, Any]
    offered_email: str


class DeclaredInputLimitsStatements:
    def __init__(
        self,
        auth_client: AuthClient,
        auth_statements: AuthStatements,
        outbox_database: OutboxDatabase,
    ):
        self.auth_client = auth_client
        self.auth_statements = auth_statements
        self.outbox_database = outbox_database

    def an_identifier_of_no_live_challenge(self) -> str:
        return str(uuid.uuid4())

    async def request_code_with_an_email_of_255_octets(self) -> Rejection:
        offered = _ascii_email_of_octets(OVERSIZED_EMAIL_OCTETS)
        return await self._start("email на запросе кода длиной 255 октетов при лимите 254", offered)

    async def request_code_with_a_multibyte_email_over_the_octet_limit(self) -> Rejection:
        offered = _multibyte_email_inside_the_character_limit()
        return await self._start("многобайтовый email в 254 символа, но не в 254 октета", offered)

    async def request_code_with_a_body_of_several_megabytes(self) -> Rejection:
        offered = _several_megabytes_of(ASCII_FILLER)
        return await self._start("тело запроса кода на несколько мегабайт", offered)

    async def verify_a_code_of_seven_digits(self) -> Rejection:
        return await self._verify("код на проверке из 7 цифр", SEVEN_DIGIT_CODE)

    async def verify_with_a_body_of_several_megabytes(self) -> Rejection:
        return await self._verify("тело запроса проверки на несколько мегабайт", _several_megabytes_of(DIGIT_FILLER))

    def assert_rejected_as_invalid_data(self, rejection: Rejection) -> None:
        assert rejection.http_status == HTTP_BAD_REQUEST, (
            f"«{rejection.label}» must be refused as invalid data with {HTTP_BAD_REQUEST}, "
            f"got {rejection.http_status} with body {self._trimmed(rejection.body)}"
        )
        assert rejection.body.get("code") == VALIDATION_FAILED, (
            f"«{rejection.label}» must answer error code {VALIDATION_FAILED}, got {rejection.body.get('code')!r}"
        )
        assert frozenset(rejection.body) == ERROR_ENVELOPE_FIELDS, (
            f"«{rejection.label}» must answer exactly {sorted(ERROR_ENVELOPE_FIELDS)}, got {sorted(rejection.body)}"
        )

    async def assert_no_request_was_queued(self, rejection: Rejection) -> None:
        queued = await self.outbox_database.queued_code_for(rejection.offered_email)
        assert queued is None, f"«{rejection.label}» must queue nothing, found code {queued!r} in the outbox"

    def assert_no_live_challenge_was_created(self, rejection: Rejection) -> None:
        assert CHALLENGE_ID_FIELD not in rejection.body, (
            f"«{rejection.label}» must create no live challenge, "
            f"the answer carried {CHALLENGE_ID_FIELD} {rejection.body.get(CHALLENGE_ID_FIELD)!r}"
        )

    def assert_carries_neither_session_nor_token(self, rejection: Rejection) -> None:
        rendered = repr(rejection.body)
        leaked = [name for name in SESSION_BEARING_NAMES if name in rendered]
        assert not leaked, (
            f"«{rejection.label}» must carry neither a session nor a token, "
            f"found {leaked!r} in {self._trimmed(rejection.body)}"
        )

    async def assert_a_valid_request_is_still_accepted(self) -> None:
        challenge = await self.auth_statements.request_code(self.auth_statements.new_user_email())
        self.auth_statements.assert_challenge_accepted(challenge)

    async def _start(self, label: str, offered_email: str) -> Rejection:
        body = {EMAIL_FIELD: offered_email, CHALLENGE_TYPE_FIELD: EMAIL_CODE}
        response = await self.auth_client.post(CHALLENGE_START_PATH, json=body)
        return Rejection(label, response.status_code, self._body_of(response), offered_email)

    async def _verify(self, label: str, code: str) -> Rejection:
        body = {CHALLENGE_ID_FIELD: self.an_identifier_of_no_live_challenge(), CODE_FIELD: code}
        response = await self.auth_client.post(CHALLENGE_VERIFY_PATH, json=body)
        return Rejection(label, response.status_code, self._body_of(response), NO_ADDRESS)

    @staticmethod
    def _trimmed(body: dict[str, Any]) -> str:
        return repr(body)[:400]

    @staticmethod
    def _body_of(response: Response) -> dict[str, Any]:
        try:
            parsed = response.json()
        except ValueError:
            return {}
        return parsed if isinstance(parsed, dict) else {}
