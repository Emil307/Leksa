from dataclasses import dataclass

from clients.application.auth_client import AuthClient
from clients.application.dto.auth.session_dto import SessionDto
from clients.application.dto.auth.session_refusal_dto import SessionRefusalDto
from clients.application.dto.profile.profile_dto import ProfileDto
from clients.application.profile_client import ProfileClient

from statements.auth_database import AuthDatabase
from statements.auth_statements import assert_exactly_one_session
from statements.profile_statements import assert_profile_of_user_returned
from statements.session_refresh_statements import SessionRefreshStatements
from statements.session_rotation_consistency_statements import (
    LiveStoredSession,
    Rotation,
    SessionRotationConsistencyStatements,
)
from statements.stored_session_row import StoredSessionRow, assert_stored_row_unchanged
from statements.wire_contract import assert_unified_authorization_refusal

LOST_PAIR_TOKEN = "the access token of the lost rotation response"


@dataclass(frozen=True)
class LostRotation:
    live: LiveStoredSession
    committed: Rotation


@dataclass(frozen=True)
class OldTokenReplay:
    refusal: SessionRefusalDto
    row_after: StoredSessionRow
    session_ids_after: list[str]


@dataclass(frozen=True)
class LostPairUsage:
    profile: ProfileDto
    next_rotation: SessionDto


class LostRotationResponseStatements:
    def __init__(
        self,
        auth_client: AuthClient,
        session_refresh_statements: SessionRefreshStatements,
        session_rotation_consistency_statements: SessionRotationConsistencyStatements,
        profile_client: ProfileClient,
        auth_database: AuthDatabase,
    ):
        self.auth_client = auth_client
        self.session_refresh_statements = session_refresh_statements
        self.session_rotation_consistency_statements = session_rotation_consistency_statements
        self.profile_client = profile_client
        self.auth_database = auth_database

    async def given_committed_rotation_whose_response_was_lost(self) -> LostRotation:
        live = await self.session_rotation_consistency_statements.given_live_session_in_real_storage()
        committed = await self.session_rotation_consistency_statements.rotate_tokens_through_the_application(live)
        self.session_rotation_consistency_statements.assert_rotation_answered_with_same_session_and_new_pair(
            live, committed
        )
        self.session_rotation_consistency_statements.assert_same_row_stores_new_token_and_new_expiry(live, committed)
        return LostRotation(live=live, committed=committed)

    async def replay_with_old_refresh_token(self, lost: LostRotation) -> OldTokenReplay:
        refusal = await self.auth_client.refresh_session_capturing_refusal(lost.live.session.refresh_token)
        row_after = await self.auth_database.stored_session_row(lost.live.session.session_id)
        session_ids_after = await self.auth_database.session_ids_of_user(lost.live.session.user_id)
        return OldTokenReplay(refusal=refusal, row_after=row_after, session_ids_after=session_ids_after)

    def assert_replay_is_refused_with_unified_error(self, replay: OldTokenReplay) -> None:
        assert_unified_authorization_refusal(replay.refusal.http_status, replay.refusal.body)

    def assert_storage_holds_exactly_the_committed_rotation(self, lost: LostRotation, replay: OldTokenReplay) -> None:
        assert_exactly_one_session(
            replay.session_ids_after, lost.live.session.session_id, f"replaying the old token of {lost.live.email}"
        )
        assert_stored_row_unchanged(
            lost.committed.stored_after,
            replay.row_after,
            f"the replay after the committed rotation of session {lost.live.session.session_id!r}",
        )

    def assert_replay_did_not_replace_the_lost_pair(self, lost: LostRotation, replay: OldTokenReplay) -> None:
        assert replay.row_after.refresh_token == lost.committed.session.refresh_token, (
            f"the row of session {lost.live.session.session_id!r} must still hold the refresh token "
            "the lost response answered with, the storage holds another token"
        )

    async def use_the_lost_pair_after_the_replay(self, lost: LostRotation) -> LostPairUsage:
        profile = await self.profile_client.fetch_profile(lost.committed.session.access_token)
        next_rotation = await self.auth_client.refresh_session(lost.committed.session.refresh_token)
        return LostPairUsage(profile=profile, next_rotation=next_rotation)

    def assert_lost_access_token_still_opens_the_profile(self, lost: LostRotation, usage: LostPairUsage) -> None:
        assert_profile_of_user_returned(usage.profile, lost.live.session.user_id, LOST_PAIR_TOKEN)
        assert usage.profile.record.email == lost.live.email, (
            f"the profile answered to {LOST_PAIR_TOKEN} must carry the email {lost.live.email!r}, "
            f"got {usage.profile.record.email!r}"
        )

    def assert_lost_refresh_token_still_rotates_the_same_session(
        self, lost: LostRotation, usage: LostPairUsage
    ) -> None:
        self.session_refresh_statements.assert_rotation_succeeded(usage.next_rotation)
        self.session_refresh_statements.assert_session_identifier_is_unchanged(lost.live.session, usage.next_rotation)
        self.session_refresh_statements.assert_both_tokens_are_new(lost.committed.session, usage.next_rotation)
