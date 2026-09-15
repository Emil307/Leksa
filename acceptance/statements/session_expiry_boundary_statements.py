from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any

from clients.application.auth_client import AuthClient
from clients.application.dto.auth.session_dto import SessionDto
from clients.application.dto.auth.session_refusal_dto import SessionRefusalDto

from statements.auth_database import AuthDatabase
from statements.auth_statements import assert_access_token_issued_for
from statements.session_refresh_statements import SessionRefreshStatements
from statements.stored_session_row import StoredSessionRow, assert_stored_row_unchanged
from statements.test_data import TestData
from statements.user_records import user_record
from statements.wire_contract import REQUEST_TIMEOUT_SECONDS, SESSION_LIFETIME, assert_unified_authorization_refusal

JUST_BEFORE_THE_DEADLINE = timedelta(seconds=REQUEST_TIMEOUT_SECONDS)
AT_THE_DEADLINE = timedelta(0)
JUST_AFTER_THE_DEADLINE = timedelta(microseconds=-1)

TOKEN_BEARING_NAMES = ("session", "accessToken", "refreshToken", "token")
TOKEN_OF_THE_DEADLINE_ROTATION = "the access token rotated just before the deadline"


@dataclass(frozen=True)
class SessionAtDeadline:
    user_id: str
    session_id: str
    stored: StoredSessionRow


@dataclass(frozen=True)
class DeadlineRotation:
    session: SessionDto
    requested_at: datetime
    responded_at: datetime


@dataclass(frozen=True)
class DeadlineRefusal:
    refusal: SessionRefusalDto
    row_after: StoredSessionRow


class SessionExpiryBoundaryStatements:
    def __init__(
        self,
        auth_client: AuthClient,
        session_refresh_statements: SessionRefreshStatements,
        auth_database: AuthDatabase,
    ):
        self.auth_client = auth_client
        self.session_refresh_statements = session_refresh_statements
        self.auth_database = auth_database

    async def given_session_expiring_just_after_the_request(self) -> SessionAtDeadline:
        return await self._given_session_expiring_in(JUST_BEFORE_THE_DEADLINE)

    async def given_session_expiring_at_this_very_moment(self) -> SessionAtDeadline:
        return await self._given_session_expiring_in(AT_THE_DEADLINE)

    async def given_session_expired_a_microsecond_ago(self) -> SessionAtDeadline:
        return await self._given_session_expiring_in(JUST_AFTER_THE_DEADLINE)

    async def rotate_tokens(self, subject: SessionAtDeadline) -> DeadlineRotation:
        requested_at = datetime.now(UTC)
        session = await self.auth_client.refresh_session(subject.stored.refresh_token)
        responded_at = datetime.now(UTC)
        return DeadlineRotation(session=session, requested_at=requested_at, responded_at=responded_at)

    async def rotate_tokens_capturing_refusal(self, subject: SessionAtDeadline) -> DeadlineRefusal:
        refusal = await self.auth_client.refresh_session_capturing_refusal(subject.stored.refresh_token)
        row_after = await self.auth_database.stored_session_row(subject.session_id)
        return DeadlineRefusal(refusal=refusal, row_after=row_after)

    def assert_rotation_succeeded_for_the_same_session(
        self, subject: SessionAtDeadline, rotation: DeadlineRotation
    ) -> None:
        self.session_refresh_statements.assert_rotation_succeeded(rotation.session)
        assert rotation.session.session_id == subject.session_id, (
            f"the rotation just before the deadline must keep session {subject.session_id!r}, "
            f"got {rotation.session.session_id!r}"
        )
        assert rotation.session.refresh_token, "the rotation just before the deadline must answer with a refresh token"
        assert rotation.session.refresh_token != subject.stored.refresh_token, (
            "the rotation just before the deadline must issue a new refresh token, the presented one came back"
        )
        assert_access_token_issued_for(
            rotation.session.access_token,
            subject.user_id,
            subject.session_id,
            rotation.requested_at,
            rotation.responded_at,
            TOKEN_OF_THE_DEADLINE_ROTATION,
        )

    def assert_refused_with_unified_authorization_error(self, refused: DeadlineRefusal) -> None:
        assert_unified_authorization_refusal(refused.refusal.http_status, refused.refusal.body)

    def assert_session_token_and_deadline_are_untouched(
        self, subject: SessionAtDeadline, refused: DeadlineRefusal
    ) -> None:
        assert_stored_row_unchanged(
            subject.stored, refused.row_after, f"the refused rotation of session {subject.session_id!r}"
        )

    def assert_no_token_pair_was_issued(self, refused: DeadlineRefusal) -> None:
        leaked = [name for name in TOKEN_BEARING_NAMES if name in self._names_within(refused.refusal.body)]
        assert not leaked, (
            f"the refused rotation must issue no token pair, found {leaked!r} in {refused.refusal.body!r}"
        )

    async def _given_session_expiring_in(self, remaining: timedelta) -> SessionAtDeadline:
        record = user_record(name=TestData.unique_name("deadline"), email=TestData.unique_email("deadline"))
        await self.auth_database.store_user(record)
        expires_at = datetime.now(UTC) + remaining
        session_id = await self.auth_database.open_session(
            user_id=record.id, opened_at=expires_at - SESSION_LIFETIME, expires_at=expires_at
        )
        stored = await self.auth_database.stored_session_row(session_id)
        return SessionAtDeadline(user_id=record.id, session_id=session_id, stored=stored)

    @classmethod
    def _names_within(cls, body: Any) -> set[str]:
        if isinstance(body, dict):
            return set(body) | {name for value in body.values() for name in cls._names_within(value)}
        if isinstance(body, list):
            return {name for value in body for name in cls._names_within(value)}
        return set()
