import asyncio
from dataclasses import dataclass
from datetime import UTC, datetime

from clients.application.auth_client import AuthClient
from clients.application.dto.auth.session_dto import SessionDto
from clients.application.dto.auth.session_refresh_outcome_dto import SessionRefreshOutcomeDto
from clients.application.dto.profile.profile_dto import ProfileDto
from clients.application.profile_client import ProfileClient

from statements.auth_database import AuthDatabase
from statements.auth_statements import (
    assert_access_token_issued_for,
    assert_exactly_one_session,
)
from statements.profile_statements import assert_profile_of_user_returned
from statements.session_refresh_statements import SessionRefreshStatements
from statements.session_rotation_consistency_statements import (
    LiveStoredSession,
    SessionRotationConsistencyStatements,
    assert_row_stores_rotation,
    wait_for_the_second_after,
)
from statements.stored_session_row import StoredSessionRow
from statements.wire_contract import (
    HTTP_OK,
    HTTP_UNAUTHORIZED,
    assert_unified_authorization_refusal,
)

CONCURRENT_ROTATIONS = 2
RACE_STATUSES = sorted([HTTP_OK, HTTP_UNAUTHORIZED])
WINNING_TOKEN = "the access token of the winning rotation"


@dataclass(frozen=True)
class RotationRace:
    live: LiveStoredSession
    outcomes: list[SessionRefreshOutcomeDto]
    requested_at: datetime
    responded_at: datetime
    stored_after: StoredSessionRow
    session_ids_after: list[str]

    def winner(self) -> SessionDto:
        winners = [outcome.session for outcome in self.outcomes if outcome.session.http_status == HTTP_OK]
        assert len(winners) == 1, f"exactly one rotation must win the race, got {self.statuses()}"
        return winners[0]

    def loser(self) -> SessionRefreshOutcomeDto:
        losers = [outcome for outcome in self.outcomes if outcome.session.http_status != HTTP_OK]
        assert len(losers) == 1, f"exactly one rotation must lose the race, got {self.statuses()}"
        return losers[0]

    def statuses(self) -> list[int]:
        return sorted(outcome.session.http_status for outcome in self.outcomes)


class ConcurrentRotationStatements:
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

    async def given_live_session_in_real_storage(self) -> LiveStoredSession:
        return await self.session_rotation_consistency_statements.given_live_session_in_real_storage()

    async def release_two_rotations_with_the_same_token_together(self, live: LiveStoredSession) -> RotationRace:
        await wait_for_the_second_after(live.stored.created_at)
        released = [
            self.auth_client.refresh_session_capturing_outcome(live.session.refresh_token)
            for _ in range(CONCURRENT_ROTATIONS)
        ]
        requested_at = datetime.now(UTC)
        outcomes = list(await asyncio.gather(*released))
        responded_at = datetime.now(UTC)
        stored_after = await self.auth_database.stored_session_row(live.session.session_id)
        session_ids_after = await self.auth_database.session_ids_of_user(live.session.user_id)
        return RotationRace(
            live=live,
            outcomes=outcomes,
            requested_at=requested_at,
            responded_at=responded_at,
            stored_after=stored_after,
            session_ids_after=session_ids_after,
        )

    def assert_exactly_one_answer_is_successful(self, live: LiveStoredSession, race: RotationRace) -> None:
        assert race.statuses() == RACE_STATUSES, (
            f"two simultaneous rotations of one refresh token must answer exactly {RACE_STATUSES}, "
            f"got {race.statuses()} — bodies {[outcome.body for outcome in race.outcomes]}"
        )
        self.session_refresh_statements.assert_session_identifier_is_unchanged(live.session, race.winner())
        self.session_refresh_statements.assert_both_tokens_are_new(live.session, race.winner())

    def assert_the_other_answer_is_the_unified_authorization_refusal(self, race: RotationRace) -> None:
        loser = race.loser()
        assert_unified_authorization_refusal(loser.session.http_status, loser.body)

    def assert_exactly_one_full_rotation_is_stored(self, live: LiveStoredSession, race: RotationRace) -> None:
        assert_row_stores_rotation(
            live.stored,
            race.stored_after,
            race.winner(),
            race.requested_at,
            race.responded_at,
            f"session {live.session.session_id!r} after the race",
        )
        assert_exactly_one_session(
            race.session_ids_after, live.session.session_id, "two simultaneous rotations of one refresh token"
        )

    def assert_winning_access_token_verifies_with_previous_user_and_session(
        self, live: LiveStoredSession, race: RotationRace
    ) -> None:
        assert_access_token_issued_for(
            race.winner().access_token,
            live.session.user_id,
            live.session.session_id,
            race.requested_at,
            race.responded_at,
            WINNING_TOKEN,
        )

    async def request_profile_with_the_winning_access_token(self, race: RotationRace) -> ProfileDto:
        return await self.profile_client.fetch_profile(race.winner().access_token)

    def assert_profile_of_the_winning_session_returned(self, profile: ProfileDto, live: LiveStoredSession) -> None:
        assert_profile_of_user_returned(profile, live.session.user_id, WINNING_TOKEN)

    async def rotate_again_with_the_winning_refresh_token(self, race: RotationRace) -> SessionDto:
        return await self.auth_client.refresh_session(race.winner().refresh_token)

    def assert_winning_refresh_token_rotated_the_same_session(
        self, live: LiveStoredSession, race: RotationRace, rotated: SessionDto
    ) -> None:
        self.session_refresh_statements.assert_rotation_succeeded(rotated)
        self.session_refresh_statements.assert_session_identifier_is_unchanged(live.session, rotated)
        self.session_refresh_statements.assert_both_tokens_are_new(race.winner(), rotated)
