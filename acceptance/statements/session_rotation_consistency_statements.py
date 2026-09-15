import asyncio
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from clients.application.auth_client import AuthClient
from clients.application.dto.auth.session_dto import SessionDto
from clients.application.dto.auth.session_refusal_dto import SessionRefusalDto
from clients.application.dto.profile.profile_dto import ProfileDto
from clients.application.profile_client import ProfileClient

from statements.access_token import ROTATED_TOKEN
from statements.auth_database import AuthDatabase
from statements.auth_statements import (
    AuthStatements,
    assert_access_token_issued_for,
    assert_exactly_one_session,
    assert_instant_is_the_moment_plus_lifetime,
)
from statements.profile_statements import assert_profile_of_user_returned
from statements.session_refresh_statements import SessionRefreshStatements
from statements.stored_session_row import StoredSessionRow, assert_stored_row_unchanged
from statements.wire_contract import REFRESH_TOKEN_LIFETIME_VARIABLE, assert_unified_authorization_refusal


def assert_row_stores_rotation(
    before: StoredSessionRow,
    after: StoredSessionRow,
    rotated: SessionDto,
    requested_at: datetime,
    responded_at: datetime,
    subject: str,
) -> None:
    assert after.refresh_token == rotated.refresh_token, (
        f"the row of {subject} must store the refresh token the rotation answered with, the storage holds another token"
    )
    assert_instant_is_the_moment_plus_lifetime(
        after.expires_at,
        requested_at,
        responded_at,
        REFRESH_TOKEN_LIFETIME_VARIABLE,
        f"the expiry of the row of {subject}",
    )
    assert after.expires_at > before.expires_at, (
        f"the rotation must move the expiry of {subject} forward, stored {before.expires_at.isoformat()} stayed"
    )


async def wait_for_the_second_after(moment: datetime) -> None:
    next_second = moment.replace(microsecond=0) + timedelta(seconds=1)
    await asyncio.sleep(max(0.0, (next_second - datetime.now(UTC)).total_seconds()))


@dataclass(frozen=True)
class LiveStoredSession:
    email: str
    session: SessionDto
    stored: StoredSessionRow


@dataclass(frozen=True)
class Rotation:
    session: SessionDto
    requested_at: datetime
    responded_at: datetime
    stored_after: StoredSessionRow
    session_ids_after: list[str]


@dataclass(frozen=True)
class OldTokenRetry:
    refusal: SessionRefusalDto
    row_before: StoredSessionRow
    row_after: StoredSessionRow


class SessionRotationConsistencyStatements:
    def __init__(
        self,
        auth_client: AuthClient,
        auth_statements: AuthStatements,
        session_refresh_statements: SessionRefreshStatements,
        profile_client: ProfileClient,
        auth_database: AuthDatabase,
    ):
        self.auth_client = auth_client
        self.auth_statements = auth_statements
        self.session_refresh_statements = session_refresh_statements
        self.profile_client = profile_client
        self.auth_database = auth_database

    async def given_live_session_in_real_storage(self) -> LiveStoredSession:
        email = self.auth_statements.new_user_email()
        session = await self.auth_statements.given_live_session_of(email)
        stored = await self.auth_database.stored_session_row(session.session_id)
        assert stored.refresh_token == session.refresh_token, (
            f"the stored row of session {session.session_id!r} must hold the issued refresh token, "
            "the storage holds another token"
        )
        return LiveStoredSession(email=email, session=session, stored=stored)

    async def given_rotated_live_session(self) -> LiveStoredSession:
        live = await self.given_live_session_in_real_storage()
        rotation = await self.rotate_tokens_through_the_application(live)
        self.assert_rotation_answered_with_same_session_and_new_pair(live, rotation)
        return live

    async def rotate_tokens_through_the_application(self, live: LiveStoredSession) -> Rotation:
        await wait_for_the_second_after(live.stored.created_at)
        requested_at = datetime.now(UTC)
        session = await self.auth_client.refresh_session(live.session.refresh_token)
        responded_at = datetime.now(UTC)
        stored_after = await self.auth_database.stored_session_row(live.session.session_id)
        session_ids_after = await self.auth_database.session_ids_of_user(live.session.user_id)
        return Rotation(
            session=session,
            requested_at=requested_at,
            responded_at=responded_at,
            stored_after=stored_after,
            session_ids_after=session_ids_after,
        )

    def assert_rotation_answered_with_same_session_and_new_pair(
        self, live: LiveStoredSession, rotation: Rotation
    ) -> None:
        self.session_refresh_statements.assert_rotation_succeeded(rotation.session)
        self.session_refresh_statements.assert_session_identifier_is_unchanged(live.session, rotation.session)
        self.session_refresh_statements.assert_both_tokens_are_new(live.session, rotation.session)

    def assert_same_row_stores_new_token_and_new_expiry(self, live: LiveStoredSession, rotation: Rotation) -> None:
        assert_row_stores_rotation(
            live.stored,
            rotation.stored_after,
            rotation.session,
            rotation.requested_at,
            rotation.responded_at,
            f"session {live.session.session_id!r}",
        )

    def assert_no_other_session_row_was_opened(self, live: LiveStoredSession, rotation: Rotation) -> None:
        assert_exactly_one_session(
            rotation.session_ids_after, live.session.session_id, f"rotating the session of {live.email}"
        )

    def assert_new_access_token_verifies_with_previous_user_and_session(
        self, live: LiveStoredSession, rotation: Rotation
    ) -> None:
        assert_access_token_issued_for(
            rotation.session.access_token,
            live.session.user_id,
            live.session.session_id,
            rotation.requested_at,
            rotation.responded_at,
            ROTATED_TOKEN,
        )

    async def request_profile_with_rotated_token(self, rotation: Rotation) -> ProfileDto:
        return await self.profile_client.fetch_profile(rotation.session.access_token)

    def assert_profile_of_rotated_session_returned(self, profile: ProfileDto, live: LiveStoredSession) -> None:
        assert_profile_of_user_returned(profile, live.session.user_id, ROTATED_TOKEN)
        assert profile.record.email == live.email, (
            f"the profile answered to {ROTATED_TOKEN} must carry the email {live.email!r} of the rotated session, "
            f"got {profile.record.email!r}"
        )

    async def retry_with_old_refresh_token(self, live: LiveStoredSession) -> OldTokenRetry:
        row_before = await self.auth_database.stored_session_row(live.session.session_id)
        refusal = await self.auth_client.refresh_session_capturing_refusal(live.session.refresh_token)
        row_after = await self.auth_database.stored_session_row(live.session.session_id)
        return OldTokenRetry(refusal=refusal, row_before=row_before, row_after=row_after)

    def assert_retry_is_refused_with_unified_envelope(self, retry: OldTokenRetry) -> None:
        assert_unified_authorization_refusal(retry.refusal.http_status, retry.refusal.body)

    def assert_stored_row_is_unchanged_by_the_retry(self, retry: OldTokenRetry) -> None:
        assert_stored_row_unchanged(retry.row_before, retry.row_after, "the refused retry")
