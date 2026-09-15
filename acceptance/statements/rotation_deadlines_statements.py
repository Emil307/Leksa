from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from clients.application.auth_client import AuthClient
from clients.application.dto.auth.session_dto import SessionDto

from statements.access_token import ROTATED_TOKEN, expiry_of_token
from statements.auth_database import AuthDatabase
from statements.auth_statements import AuthStatements, assert_access_token_issued_for, required_seconds
from statements.session_refresh_statements import SessionRefreshStatements
from statements.stored_session_row import StoredSessionRow
from statements.wire_contract import ACCESS_TOKEN_LIFETIME_VARIABLE, REFRESH_TOKEN_LIFETIME_VARIABLE

SESSION_DEADLINE = "the rotated session deadline"
NO_UTC_OFFSET = timedelta(0)


@dataclass(frozen=True)
class RotationDeadlines:
    previous: SessionDto
    rotated: SessionDto
    requested_at: datetime
    responded_at: datetime
    stored_after: StoredSessionRow

    def access_deadline(self) -> datetime:
        return expiry_of_token(self.rotated.access_token, ROTATED_TOKEN)

    def session_deadline(self) -> datetime:
        return self.stored_after.expires_at

    def rotation_moment(self) -> datetime:
        return self.access_deadline() - timedelta(seconds=required_seconds(ACCESS_TOKEN_LIFETIME_VARIABLE))


class RotationDeadlinesStatements:
    def __init__(
        self,
        auth_client: AuthClient,
        auth_statements: AuthStatements,
        session_refresh_statements: SessionRefreshStatements,
        auth_database: AuthDatabase,
    ):
        self.auth_client = auth_client
        self.auth_statements = auth_statements
        self.session_refresh_statements = session_refresh_statements
        self.auth_database = auth_database

    async def given_live_session(self) -> SessionDto:
        return await self.auth_statements.given_live_session()

    async def rotate_tokens(self, previous: SessionDto) -> RotationDeadlines:
        requested_at = datetime.now(UTC)
        rotated = await self.auth_client.refresh_session(previous.refresh_token)
        responded_at = datetime.now(UTC)
        self.session_refresh_statements.assert_rotation_succeeded(rotated)
        stored_after = await self.auth_database.stored_session_row(previous.session_id)
        return RotationDeadlines(
            previous=previous,
            rotated=rotated,
            requested_at=requested_at,
            responded_at=responded_at,
            stored_after=stored_after,
        )

    def assert_new_access_token_belongs_to_previous_user_and_session(self, deadlines: RotationDeadlines) -> None:
        self.session_refresh_statements.assert_session_identifier_is_unchanged(deadlines.previous, deadlines.rotated)
        self.session_refresh_statements.assert_both_tokens_are_new(deadlines.previous, deadlines.rotated)
        assert_access_token_issued_for(
            deadlines.rotated.access_token,
            deadlines.previous.user_id,
            deadlines.previous.session_id,
            deadlines.requested_at,
            deadlines.responded_at,
            ROTATED_TOKEN,
        )

    def assert_access_deadline_is_rotation_moment_plus_access_lifetime(self, deadlines: RotationDeadlines) -> None:
        earliest = deadlines.requested_at.replace(microsecond=0)
        moment = deadlines.rotation_moment()
        assert earliest <= moment <= deadlines.responded_at, (
            f"{ROTATED_TOKEN} expiry minus {ACCESS_TOKEN_LIFETIME_VARIABLE} must name the rotation moment inside "
            f"[{earliest.isoformat()}, {deadlines.responded_at.isoformat()}], got {moment.isoformat()}"
        )

    def assert_session_deadline_is_rotation_moment_plus_refresh_lifetime(self, deadlines: RotationDeadlines) -> None:
        expected = deadlines.rotation_moment() + timedelta(seconds=required_seconds(REFRESH_TOKEN_LIFETIME_VARIABLE))
        actual = deadlines.session_deadline()
        assert actual == expected, (
            f"{SESSION_DEADLINE} must be exactly the rotation moment of {ROTATED_TOKEN} plus "
            f"{REFRESH_TOKEN_LIFETIME_VARIABLE} — {expected.isoformat()} — got {actual.isoformat()}"
        )

    def assert_both_deadlines_are_whole_utc_seconds(self, deadlines: RotationDeadlines) -> None:
        access = deadlines.access_deadline()
        session = deadlines.session_deadline()
        assert access.microsecond == 0, f"{ROTATED_TOKEN} expiry must be a whole second, got {access.isoformat()}"
        assert session.microsecond == 0, f"{SESSION_DEADLINE} must be a whole second, got {session.isoformat()}"
        assert session.utcoffset() == NO_UTC_OFFSET, (
            f"{SESSION_DEADLINE} must be stored in UTC, got offset {session.utcoffset()!r}"
        )
