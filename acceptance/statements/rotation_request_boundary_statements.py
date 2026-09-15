import uuid
from dataclasses import dataclass
from typing import Any

from clients.application.auth_client import AuthClient
from clients.application.dto.auth.session_dto import SessionDto
from clients.application.dto.auth.session_refusal_dto import SessionRefusalDto

from statements.auth_statements import AuthStatements, assert_exactly_one_session
from statements.session_lookup_database import SessionLookupDatabase
from statements.stored_session_row import StoredSessionRow, assert_stored_row_unchanged
from statements.wire_contract import MAX_TOKEN_BYTES, assert_validation_refusal

FORBIDDEN_SERVER_FIELDS = ("id", "user", "userId", "status", "expires_at", "accessToken")
OVERSIZED_PADDING = "a"
MULTIBYTE_TAIL = "-токен-ünï"
UNPRINTABLE_TAIL = "\x07\x1b"
FORGED_LOG_ENTRY = '\r\n{"event":"session.rotated","sid":"forged"}'
NO_ROWS = 0


@dataclass(frozen=True)
class HostileRefresh:
    label: str
    marker: str
    session: SessionDto
    payload: dict[str, Any]


@dataclass(frozen=True)
class BoundaryAttempt:
    request: HostileRefresh
    row_before: StoredSessionRow
    refusal: SessionRefusalDto
    row_after: StoredSessionRow
    session_ids_after: list[str]
    rows_carrying_marker: int

    @property
    def label(self) -> str:
        return self.request.label

    @property
    def marker(self) -> str:
        return self.request.marker


def _fresh_marker() -> str:
    return f"hostile-{uuid.uuid4().hex}"


class RotationRequestBoundaryStatements:
    def __init__(
        self,
        auth_client: AuthClient,
        auth_statements: AuthStatements,
        session_lookup_database: SessionLookupDatabase,
    ):
        self.auth_client = auth_client
        self.auth_statements = auth_statements
        self.session_lookup_database = session_lookup_database

    async def given_live_session(self) -> SessionDto:
        return await self.auth_statements.given_live_session()

    async def refresh_with_forbidden_server_field(self, session: SessionDto, field: str) -> BoundaryAttempt:
        marker = _fresh_marker()
        payload = {"refreshToken": session.refresh_token, field: marker}
        return await self._attempt(HostileRefresh(f"запрещённое серверное поле {field}", marker, session, payload))

    async def refresh_with_oversized_token(self, session: SessionDto) -> BoundaryAttempt:
        marker = _fresh_marker()
        token = marker + OVERSIZED_PADDING * (MAX_TOKEN_BYTES + 1 - len(marker))
        return await self._attempt(
            HostileRefresh("refresh-токен длиннее допустимого", marker, session, {"refreshToken": token})
        )

    async def refresh_with_multibyte_token(self, session: SessionDto) -> BoundaryAttempt:
        marker = _fresh_marker()
        return await self._attempt(
            HostileRefresh("многобайтовый refresh-токен", marker, session, {"refreshToken": marker + MULTIBYTE_TAIL})
        )

    async def refresh_with_unprintable_token(self, session: SessionDto) -> BoundaryAttempt:
        marker = _fresh_marker()
        return await self._attempt(
            HostileRefresh("непечатный refresh-токен", marker, session, {"refreshToken": marker + UNPRINTABLE_TAIL})
        )

    async def refresh_with_forged_log_entry_token(self, session: SessionDto) -> BoundaryAttempt:
        marker = _fresh_marker()
        return await self._attempt(
            HostileRefresh(
                "refresh-токен с переводом строки и поддельной записью",
                marker,
                session,
                {"refreshToken": marker + FORGED_LOG_ENTRY},
            )
        )

    def assert_refused_at_the_request_boundary(self, attempt: BoundaryAttempt) -> None:
        self.assert_refused_as_validation_failure(attempt)
        self.assert_session_row_is_unchanged(attempt)
        self.assert_no_session_carries_the_marker(attempt)
        self.assert_marker_is_not_echoed(attempt)

    def assert_refused_as_validation_failure(self, attempt: BoundaryAttempt) -> None:
        assert_validation_refusal(attempt.refusal.http_status, attempt.refusal.body, f"«{attempt.label}»")

    def assert_marker_is_not_echoed(self, attempt: BoundaryAttempt) -> None:
        assert attempt.marker not in attempt.refusal.raw_text, (
            f"«{attempt.label}» must not echo the presented value {attempt.marker!r}, got {attempt.refusal.raw_text}"
        )

    def assert_session_row_is_unchanged(self, attempt: BoundaryAttempt) -> None:
        assert_stored_row_unchanged(attempt.row_before, attempt.row_after, f"«{attempt.label}»")

    def assert_no_session_carries_the_marker(self, attempt: BoundaryAttempt) -> None:
        assert attempt.rows_carrying_marker == NO_ROWS, (
            f"«{attempt.label}» must leave no session row carrying {attempt.marker!r}, "
            f"found {attempt.rows_carrying_marker}"
        )
        assert_exactly_one_session(
            attempt.session_ids_after, attempt.request.session.session_id, f"«{attempt.label}» on the refresh endpoint"
        )

    async def _attempt(self, request: HostileRefresh) -> BoundaryAttempt:
        session = request.session
        row_before = await self.session_lookup_database.stored_session_row(session.session_id)
        refusal = await self.auth_client.refresh_with_json_body(request.payload)
        return BoundaryAttempt(
            request=request,
            row_before=row_before,
            refusal=refusal,
            row_after=await self.session_lookup_database.stored_session_row(session.session_id),
            session_ids_after=await self.session_lookup_database.session_ids_of_user(session.user_id),
            rows_carrying_marker=await self.session_lookup_database.count_sessions_carrying(request.marker),
        )
