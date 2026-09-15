import secrets
from dataclasses import dataclass

from clients.application.auth_client import AuthClient
from clients.application.dto.auth.session_dto import SessionDto
from clients.application.dto.auth.session_refusal_dto import SessionRefusalDto

from statements.auth_statements import AuthStatements, assert_exactly_one_session
from statements.session_lookup_database import SessionLookupDatabase
from statements.stored_session_row import StoredSessionRow, assert_stored_row_unchanged
from statements.wire_contract import (
    HTTP_BAD_REQUEST,
    MAX_TOKEN_BYTES,
    VALIDATION_FAILED,
    assert_unified_authorization_refusal,
)

FIRST_PRINTABLE_ASCII = 0x20
LAST_PRINTABLE_ASCII = 0x7E
PRINTABLE_ASCII = "".join(chr(code) for code in range(FIRST_PRINTABLE_ASCII, LAST_PRINTABLE_ASCII + 1))


def max_length_printable_ascii_token() -> str:
    edges = chr(FIRST_PRINTABLE_ASCII) + chr(LAST_PRINTABLE_ASCII)
    middle = "".join(secrets.choice(PRINTABLE_ASCII) for _ in range(MAX_TOKEN_BYTES - len(edges)))
    token = edges[0] + middle + edges[1]
    assert len(token.encode("ascii")) == MAX_TOKEN_BYTES, (
        f"the probe token must be exactly {MAX_TOKEN_BYTES} ASCII bytes, built {len(token.encode('ascii'))}"
    )
    return token


@dataclass(frozen=True)
class UnknownMaxLengthToken:
    token: str
    control: SessionDto
    control_row: StoredSessionRow


@dataclass(frozen=True)
class MaxLengthTokenRefusal:
    refusal: SessionRefusalDto
    control_row_after: StoredSessionRow
    control_session_ids_after: list[str]


class MaxLengthRefreshTokenStatements:
    def __init__(
        self, auth_client: AuthClient, auth_statements: AuthStatements, session_lookup_database: SessionLookupDatabase
    ):
        self.auth_client = auth_client
        self.auth_statements = auth_statements
        self.session_lookup_database = session_lookup_database

    async def given_no_session_for_a_max_length_ascii_token(self) -> UnknownMaxLengthToken:
        control = await self.auth_statements.given_live_session()
        token = max_length_printable_ascii_token()
        holders = await self.session_lookup_database.session_ids_with_refresh_token(token)
        assert holders == [], f"no session may hold the {MAX_TOKEN_BYTES}-byte probe token, found {holders!r}"
        control_row = await self.session_lookup_database.stored_session_row(control.session_id)
        return UnknownMaxLengthToken(token=token, control=control, control_row=control_row)

    async def refresh_with_the_token(self, unknown: UnknownMaxLengthToken) -> MaxLengthTokenRefusal:
        refusal = await self.auth_client.refresh_session_capturing_refusal(unknown.token)
        control_row_after = await self.session_lookup_database.stored_session_row(unknown.control.session_id)
        control_session_ids_after = await self.session_lookup_database.session_ids_of_user(unknown.control.user_id)
        return MaxLengthTokenRefusal(
            refusal=refusal,
            control_row_after=control_row_after,
            control_session_ids_after=control_session_ids_after,
        )

    def assert_unified_authorization_refusal(self, outcome: MaxLengthTokenRefusal) -> None:
        assert_unified_authorization_refusal(outcome.refusal.http_status, outcome.refusal.body)

    def assert_no_validation_error(self, outcome: MaxLengthTokenRefusal) -> None:
        assert outcome.refusal.http_status != HTTP_BAD_REQUEST, (
            f"a {MAX_TOKEN_BYTES}-byte printable ASCII token must pass validation, "
            f"got {HTTP_BAD_REQUEST} with body {outcome.refusal.body!r}"
        )
        code = outcome.refusal.body.get("code") if isinstance(outcome.refusal.body, dict) else None
        assert code != VALIDATION_FAILED, (
            f"a {MAX_TOKEN_BYTES}-byte printable ASCII token must not be reported as {VALIDATION_FAILED}, "
            f"got body {outcome.refusal.body!r}"
        )

    def assert_no_session_was_changed(self, unknown: UnknownMaxLengthToken, outcome: MaxLengthTokenRefusal) -> None:
        assert_stored_row_unchanged(
            unknown.control_row,
            outcome.control_row_after,
            f"the refused probe beside session {unknown.control.session_id!r}",
        )
        assert_exactly_one_session(
            outcome.control_session_ids_after,
            unknown.control.session_id,
            f"refusing the {MAX_TOKEN_BYTES}-byte probe token beside the session of {unknown.control.user_id}",
        )
