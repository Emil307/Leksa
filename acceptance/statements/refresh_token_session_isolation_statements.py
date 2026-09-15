from dataclasses import dataclass
from datetime import UTC, datetime

from clients.application.auth_client import AuthClient
from clients.application.dto.auth.session_dto import SessionDto
from clients.application.dto.auth.session_refusal_dto import SessionRefusalDto

from statements.auth_database import AuthDatabase
from statements.auth_statements import assert_access_token_issued_for, assert_exactly_one_session
from statements.session_refresh_statements import SessionRefreshStatements
from statements.session_rotation_consistency_statements import (
    LiveStoredSession,
    SessionRotationConsistencyStatements,
    assert_row_stores_rotation,
    wait_for_the_second_after,
)
from statements.stored_session_row import StoredSessionRow, assert_stored_row_unchanged
from statements.wire_contract import assert_validation_refusal

TOKEN_OF_USER_A = "the access token answered to the refresh token of user A"


@dataclass(frozen=True)
class TwoOwners:
    user_a: LiveStoredSession
    user_b: LiveStoredSession


@dataclass(frozen=True)
class RowsAfter:
    user_a: StoredSessionRow
    user_b: StoredSessionRow
    session_ids_of_a: list[str]
    session_ids_of_b: list[str]


@dataclass(frozen=True)
class IsolatedRotation:
    rotated: SessionDto
    requested_at: datetime
    responded_at: datetime
    after: RowsAfter


@dataclass(frozen=True)
class OwnerOverrideAttempt:
    refusal: SessionRefusalDto
    after: RowsAfter


class RefreshTokenSessionIsolationStatements:
    def __init__(
        self,
        auth_client: AuthClient,
        session_rotation_consistency_statements: SessionRotationConsistencyStatements,
        session_refresh_statements: SessionRefreshStatements,
        auth_database: AuthDatabase,
    ):
        self.auth_client = auth_client
        self.session_rotation_consistency_statements = session_rotation_consistency_statements
        self.session_refresh_statements = session_refresh_statements
        self.auth_database = auth_database

    async def given_independent_live_sessions_of_users_a_and_b(self) -> TwoOwners:
        user_a = await self.session_rotation_consistency_statements.given_live_session_in_real_storage()
        user_b = await self.session_rotation_consistency_statements.given_live_session_in_real_storage()
        assert user_a.session.user_id != user_b.session.user_id, (
            f"users A and B must be distinct, both resolved to {user_a.session.user_id!r}"
        )
        return TwoOwners(user_a=user_a, user_b=user_b)

    async def rotate_with_the_token_of_user_a(self, owners: TwoOwners) -> IsolatedRotation:
        await wait_for_the_second_after(owners.user_a.stored.created_at)
        requested_at = datetime.now(UTC)
        rotated = await self.auth_client.refresh_session(owners.user_a.session.refresh_token)
        responded_at = datetime.now(UTC)
        return IsolatedRotation(
            rotated=rotated, requested_at=requested_at, responded_at=responded_at, after=await self._rows_after(owners)
        )

    def assert_only_the_session_of_user_a_was_rotated(self, owners: TwoOwners, rotation: IsolatedRotation) -> None:
        user_a = owners.user_a
        self.session_refresh_statements.assert_rotation_succeeded(rotation.rotated)
        self.session_refresh_statements.assert_session_identifier_is_unchanged(user_a.session, rotation.rotated)
        self.session_refresh_statements.assert_both_tokens_are_new(user_a.session, rotation.rotated)
        assert_row_stores_rotation(
            user_a.stored,
            rotation.after.user_a,
            rotation.rotated,
            rotation.requested_at,
            rotation.responded_at,
            f"session {user_a.session.session_id!r} of user A",
        )
        assert_access_token_issued_for(
            rotation.rotated.access_token,
            user_a.session.user_id,
            user_a.session.session_id,
            rotation.requested_at,
            rotation.responded_at,
            TOKEN_OF_USER_A,
        )
        assert_exactly_one_session(rotation.after.session_ids_of_a, user_a.session.session_id, "rotating user A")

    def assert_session_of_user_b_is_unchanged(self, owners: TwoOwners, rotation: IsolatedRotation) -> None:
        self._assert_row_of_user_b_untouched(owners, rotation.after)
        assert rotation.rotated.refresh_token != owners.user_b.stored.refresh_token, (
            "the rotation of user A must not answer with the refresh token of user B"
        )

    async def rotate_with_the_token_of_user_a_naming_user_b_as_owner(self, owners: TwoOwners) -> OwnerOverrideAttempt:
        refusal = await self.auth_client.refresh_session_naming_owner(
            owners.user_a.session.refresh_token, owners.user_b.session.user_id
        )
        return OwnerOverrideAttempt(refusal=refusal, after=await self._rows_after(owners))

    def assert_owner_identifier_is_refused_as_invalid_data(self, attempt: OwnerOverrideAttempt) -> None:
        assert_validation_refusal(attempt.refusal.http_status, attempt.refusal.body, "a refresh naming another owner")

    def assert_neither_session_was_changed(self, owners: TwoOwners, attempt: OwnerOverrideAttempt) -> None:
        assert_stored_row_unchanged(
            owners.user_a.stored, attempt.after.user_a, "the refused refresh naming user B, for the session of user A,"
        )
        self._assert_row_of_user_b_untouched(owners, attempt.after)
        assert_exactly_one_session(attempt.after.session_ids_of_a, owners.user_a.session.session_id, "refusing user A")

    def _assert_row_of_user_b_untouched(self, owners: TwoOwners, after: RowsAfter) -> None:
        user_b = owners.user_b
        assert_stored_row_unchanged(user_b.stored, after.user_b, f"the session {user_b.session.session_id!r} of user B")
        assert_exactly_one_session(after.session_ids_of_b, user_b.session.session_id, "leaving user B alone")

    async def _rows_after(self, owners: TwoOwners) -> RowsAfter:
        return RowsAfter(
            user_a=await self.auth_database.stored_session_row(owners.user_a.session.session_id),
            user_b=await self.auth_database.stored_session_row(owners.user_b.session.session_id),
            session_ids_of_a=await self.auth_database.session_ids_of_user(owners.user_a.session.user_id),
            session_ids_of_b=await self.auth_database.session_ids_of_user(owners.user_b.session.user_id),
        )
