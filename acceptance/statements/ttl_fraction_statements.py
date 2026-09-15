import asyncio
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from clients.application.auth_client import AuthClient
from clients.application.dto.auth.session_dto import SessionDto

from statements.access_token import ROTATED_TOKEN, expiry_of_token
from statements.auth_database import AuthDatabase
from statements.auth_statements import AuthStatements, required_seconds
from statements.session_refresh_statements import SessionRefreshStatements
from statements.stored_session_row import StoredSessionRow
from statements.wire_contract import ACCESS_TOKEN_LIFETIME_VARIABLE, REFRESH_TOKEN_LIFETIME_VARIABLE

HALF_A_SECOND = timedelta(milliseconds=500)
ONE_SECOND = timedelta(seconds=1)
ROTATION_ATTEMPTS = 5


def whole_second_of(moment: datetime) -> datetime:
    return moment.replace(microsecond=0)


async def wait_for_the_half_of_the_next_second() -> None:
    target = whole_second_of(datetime.now(UTC)) + ONE_SECOND + HALF_A_SECOND
    await asyncio.sleep(max(0.0, (target - datetime.now(UTC)).total_seconds()))


@dataclass(frozen=True)
class MidSecondRotation:
    rotated: SessionDto
    requested_at: datetime
    responded_at: datetime
    stored_after: StoredSessionRow


class TtlFractionStatements:
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

    async def rotate_at_the_half_of_a_second(self, session: SessionDto) -> MidSecondRotation:
        refresh_token = session.refresh_token
        for _ in range(ROTATION_ATTEMPTS):
            await wait_for_the_half_of_the_next_second()
            requested_at = datetime.now(UTC)
            rotated = await self.auth_client.refresh_session(refresh_token)
            responded_at = datetime.now(UTC)
            self.session_refresh_statements.assert_rotation_succeeded(rotated)
            refresh_token = rotated.refresh_token
            if whole_second_of(requested_at) == whole_second_of(responded_at):
                stored_after = await self.auth_database.stored_session_row(session.session_id)
                return MidSecondRotation(rotated, requested_at, responded_at, stored_after)
        raise AssertionError(
            f"the rotation must complete inside one whole second to pin its instant, "
            f"{ROTATION_ATTEMPTS} attempts each crossed a second boundary"
        )

    def assert_session_deadline_is_the_whole_second_of_the_rotation_plus_the_lifetime(
        self, rotation: MidSecondRotation
    ) -> None:
        lifetime = timedelta(seconds=required_seconds(REFRESH_TOKEN_LIFETIME_VARIABLE))
        expected = whole_second_of(rotation.requested_at) + lifetime
        actual = rotation.stored_after.expires_at
        assert actual == expected, (
            f"the session deadline must be the whole second of the rotation instant plus exactly {lifetime} "
            f"({REFRESH_TOKEN_LIFETIME_VARIABLE}) — {expected.isoformat()} — got {actual.isoformat()}"
        )

    def assert_both_deadlines_drop_the_fraction_of_the_same_second(self, rotation: MidSecondRotation) -> None:
        refresh_lifetime = timedelta(seconds=required_seconds(REFRESH_TOKEN_LIFETIME_VARIABLE))
        access_lifetime = timedelta(seconds=required_seconds(ACCESS_TOKEN_LIFETIME_VARIABLE))
        session_instant = rotation.stored_after.expires_at - refresh_lifetime
        access_instant = expiry_of_token(rotation.rotated.access_token, ROTATED_TOKEN) - access_lifetime
        assert session_instant == access_instant == whole_second_of(session_instant), (
            f"both deadlines must start from the same whole second of the rotation instant — "
            f"the session deadline implies {session_instant.isoformat()}, {ROTATED_TOKEN} implies "
            f"{access_instant.isoformat()}"
        )

    def assert_access_deadline_is_the_whole_second_of_the_rotation_plus_the_lifetime(
        self, rotation: MidSecondRotation
    ) -> None:
        lifetime = timedelta(seconds=required_seconds(ACCESS_TOKEN_LIFETIME_VARIABLE))
        expected = whole_second_of(rotation.requested_at) + lifetime
        actual = expiry_of_token(rotation.rotated.access_token, ROTATED_TOKEN)
        assert actual == expected, (
            f"{ROTATED_TOKEN} must expire at the whole second of the rotation instant plus exactly {lifetime} "
            f"({ACCESS_TOKEN_LIFETIME_VARIABLE}) — {expected.isoformat()} — got {actual.isoformat()}"
        )
