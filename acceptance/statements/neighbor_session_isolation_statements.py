from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from clients.application.auth_client import AuthClient
from clients.application.dto.auth.session_dto import SessionDto

from statements.auth_database import AuthDatabase
from statements.auth_statements import AuthStatements, required_seconds
from statements.session_refresh_statements import SessionRefreshStatements
from statements.session_rotation_consistency_statements import assert_row_stores_rotation, wait_for_the_second_after
from statements.stored_session_row import StoredSessionRow, assert_stored_row_unchanged
from statements.wire_contract import REFRESH_TOKEN_LIFETIME_VARIABLE


@dataclass(frozen=True)
class StoredSession:
    session: SessionDto
    stored: StoredSessionRow


@dataclass(frozen=True)
class Neighbor:
    user_id: str
    session_id: str
    stored: StoredSessionRow


@dataclass(frozen=True)
class Neighborhood:
    email: str
    first: StoredSession
    same_user_neighbor: Neighbor
    other_user_neighbor: Neighbor


@dataclass(frozen=True)
class FirstSessionRotation:
    session: SessionDto
    requested_at: datetime
    responded_at: datetime
    first_after: StoredSessionRow
    same_user_neighbor_after: StoredSessionRow
    other_user_neighbor_after: StoredSessionRow
    same_user_session_ids_after: list[str]
    other_user_session_ids_after: list[str]


class NeighborSessionIsolationStatements:
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

    async def given_first_session_beside_two_neighbors(self) -> Neighborhood:
        email = self.auth_statements.new_user_email()
        first = await self.auth_statements.given_live_session_of(email)
        same_user_neighbor = await self._open_neighbor_of(first.user_id)
        other_user = await self.auth_statements.given_live_session()
        assert other_user.user_id != first.user_id, f"the neighbor of another user must not belong to {first.user_id!r}"
        other_user_neighbor = await self._neighbor(other_user.user_id, other_user.session_id)
        stored_first = await self._stored(first)
        await wait_for_the_second_after(stored_first.stored.created_at)
        return Neighborhood(
            email=email,
            first=stored_first,
            same_user_neighbor=same_user_neighbor,
            other_user_neighbor=other_user_neighbor,
        )

    async def rotate_the_first_session(self, neighborhood: Neighborhood) -> FirstSessionRotation:
        requested_at = datetime.now(UTC)
        session = await self.auth_client.refresh_session(neighborhood.first.session.refresh_token)
        responded_at = datetime.now(UTC)
        return FirstSessionRotation(
            session=session,
            requested_at=requested_at,
            responded_at=responded_at,
            first_after=await self.auth_database.stored_session_row(neighborhood.first.session.session_id),
            same_user_neighbor_after=await self._row_of(neighborhood.same_user_neighbor),
            other_user_neighbor_after=await self._row_of(neighborhood.other_user_neighbor),
            same_user_session_ids_after=await self.auth_database.session_ids_of_user(
                neighborhood.first.session.user_id
            ),
            other_user_session_ids_after=await self.auth_database.session_ids_of_user(
                neighborhood.other_user_neighbor.user_id
            ),
        )

    def assert_first_session_received_a_new_pair_and_a_new_expiry(
        self, neighborhood: Neighborhood, rotation: FirstSessionRotation
    ) -> None:
        first = neighborhood.first
        self.session_refresh_statements.assert_rotation_succeeded(rotation.session)
        self.session_refresh_statements.assert_session_identifier_is_unchanged(first.session, rotation.session)
        self.session_refresh_statements.assert_both_tokens_are_new(first.session, rotation.session)
        assert_row_stores_rotation(
            first.stored,
            rotation.first_after,
            rotation.session,
            rotation.requested_at,
            rotation.responded_at,
            f"the first session {first.session.session_id!r}",
        )

    def assert_both_neighbor_sessions_are_unchanged(
        self, neighborhood: Neighborhood, rotation: FirstSessionRotation
    ) -> None:
        self._assert_row_unchanged(
            neighborhood.same_user_neighbor, rotation.same_user_neighbor_after, "the other session of the same user"
        )
        self._assert_row_unchanged(
            neighborhood.other_user_neighbor, rotation.other_user_neighbor_after, "the session of the other user"
        )
        expected_same_user = [neighborhood.first.session.session_id, neighborhood.same_user_neighbor.session_id]
        assert rotation.same_user_session_ids_after == expected_same_user, (
            f"rotating the first session of {neighborhood.email} must leave exactly {expected_same_user!r} "
            f"in storage, found {rotation.same_user_session_ids_after!r}"
        )
        expected_other_user = [neighborhood.other_user_neighbor.session_id]
        assert rotation.other_user_session_ids_after == expected_other_user, (
            f"rotating the first session of {neighborhood.email} must leave exactly {expected_other_user!r} "
            f"for the other user, found {rotation.other_user_session_ids_after!r}"
        )

    async def _stored(self, session: SessionDto) -> StoredSession:
        return StoredSession(session=session, stored=await self.auth_database.stored_session_row(session.session_id))

    async def _open_neighbor_of(self, user_id: str) -> Neighbor:
        opened_at = datetime.now(UTC)
        lifetime = timedelta(seconds=required_seconds(REFRESH_TOKEN_LIFETIME_VARIABLE))
        session_id = await self.auth_database.open_session(
            user_id=user_id, opened_at=opened_at, expires_at=opened_at + lifetime
        )
        return await self._neighbor(user_id, session_id)

    async def _neighbor(self, user_id: str, session_id: str) -> Neighbor:
        return Neighbor(
            user_id=user_id, session_id=session_id, stored=await self.auth_database.stored_session_row(session_id)
        )

    async def _row_of(self, neighbor: Neighbor) -> StoredSessionRow:
        return await self.auth_database.stored_session_row(neighbor.session_id)

    def _assert_row_unchanged(self, before: Neighbor, after: StoredSessionRow, subject: str) -> None:
        assert_stored_row_unchanged(
            before.stored, after, f"the rotation of a neighbor of {subject} {before.session_id!r}"
        )
