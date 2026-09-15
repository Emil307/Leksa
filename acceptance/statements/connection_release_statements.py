import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from time import perf_counter

from clients.application.dto.profile.profile_dto import ProfileDto, UserRecord
from clients.application.profile_client import ProfileClient

from statements.access_token import mint_access_token
from statements.auth_database import AuthDatabase
from statements.pool_release_assertions import (
    REQUESTS_PER_OUTCOME,
    PoolAttempt,
    assert_answered_without_waiting_for_a_connection,
    assert_every_attempt_reached_its_outcome,
    assert_every_outcome_was_driven_past_pool_capacity,
    assert_no_attempt_waited_for_a_connection,
)
from statements.profile_statements import assert_profile_of_user_returned
from statements.test_data import TestData
from statements.user_records import user_record
from statements.wire_contract import ACCESS_TOKEN_LIFETIME, HTTP_OK, HTTP_UNAUTHORIZED, SESSION_LIFETIME

SESSION_OPENED_AGO = timedelta(hours=2)
SESSION_EXPIRED_AGO = timedelta(minutes=1)

LIVE_SESSION = "live session"
EXPIRED_SESSION = "expired session"
UNKNOWN_SESSION = "unknown session"


@dataclass(frozen=True)
class ProfileOutcome:
    name: str
    access_token: str
    expected_status: int


@dataclass(frozen=True)
class ProfileAttempt:
    outcome: ProfileOutcome
    profile: ProfileDto
    seconds: float


class ConnectionReleaseStatements:
    def __init__(self, profile_client: ProfileClient, auth_database: AuthDatabase):
        self.profile_client = profile_client
        self.auth_database = auth_database
        self._live_outcome: ProfileOutcome | None = None
        self._live_account: UserRecord | None = None

    async def given_pool_at_rest_and_every_reachable_outcome(self) -> list[ProfileOutcome]:
        self._live_outcome = await self._live_session_outcome()
        return [self._live_outcome, await self._expired_session_outcome(), self._unknown_session_outcome()]

    async def drive_each_outcome_past_pool_capacity(self, outcomes: list[ProfileOutcome]) -> list[ProfileAttempt]:
        return [await self._attempt(outcome) for _ in range(REQUESTS_PER_OUTCOME) for outcome in outcomes]

    def assert_every_outcome_was_driven_past_pool_capacity(self, attempts: list[ProfileAttempt]) -> None:
        assert_every_outcome_was_driven_past_pool_capacity(self._pool_attempts(attempts))

    def assert_every_attempt_reached_its_outcome(self, attempts: list[ProfileAttempt]) -> None:
        assert_every_attempt_reached_its_outcome(self._pool_attempts(attempts))

    def assert_no_attempt_waited_for_a_connection(self, attempts: list[ProfileAttempt]) -> None:
        assert_no_attempt_waited_for_a_connection(self._pool_attempts(attempts))

    async def assert_later_requests_still_obtain_a_connection(self) -> None:
        outcome, account = self._require_prepared_live_session()
        attempt = await self._attempt(outcome)
        assert_profile_of_user_returned(attempt.profile, account.id, "the request after every outcome")
        assert_answered_without_waiting_for_a_connection(attempt.seconds, "the later request")

    @staticmethod
    def _pool_attempts(attempts: list[ProfileAttempt]) -> list[PoolAttempt]:
        return [
            PoolAttempt(
                outcome_name=attempt.outcome.name,
                expected_status=attempt.outcome.expected_status,
                http_status=attempt.profile.http_status,
                seconds=attempt.seconds,
            )
            for attempt in attempts
        ]

    async def _attempt(self, outcome: ProfileOutcome) -> ProfileAttempt:
        started = perf_counter()
        profile = await self.profile_client.fetch_profile(outcome.access_token)
        return ProfileAttempt(outcome=outcome, profile=profile, seconds=perf_counter() - started)

    def _require_prepared_live_session(self) -> tuple[ProfileOutcome, UserRecord]:
        assert self._live_outcome is not None and self._live_account is not None, (
            "the live-session outcome must be prepared before a later request is driven"
        )
        return self._live_outcome, self._live_account

    async def _live_session_outcome(self) -> ProfileOutcome:
        now = datetime.now(UTC)
        account = await self._store_account()
        session_id = await self.auth_database.open_session(
            user_id=account.id, opened_at=now, expires_at=now + SESSION_LIFETIME
        )
        self._live_account = account
        return ProfileOutcome(
            name=LIVE_SESSION,
            access_token=self._token_for(account.id, session_id, now),
            expected_status=HTTP_OK,
        )

    async def _expired_session_outcome(self) -> ProfileOutcome:
        now = datetime.now(UTC)
        account = await self._store_account()
        session_id = await self.auth_database.open_session(
            user_id=account.id, opened_at=now - SESSION_OPENED_AGO, expires_at=now - SESSION_EXPIRED_AGO
        )
        return ProfileOutcome(
            name=EXPIRED_SESSION,
            access_token=self._token_for(account.id, session_id, now),
            expected_status=HTTP_UNAUTHORIZED,
        )

    def _unknown_session_outcome(self) -> ProfileOutcome:
        return ProfileOutcome(
            name=UNKNOWN_SESSION,
            access_token=self._token_for(str(uuid.uuid4()), str(uuid.uuid4()), datetime.now(UTC)),
            expected_status=HTTP_UNAUTHORIZED,
        )

    async def _store_account(self) -> UserRecord:
        account = user_record(
            name=TestData.unique_name("name"),
            email=TestData.unique_email("release"),
            is_superuser=False,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        await self.auth_database.store_user(account)
        return account

    @staticmethod
    def _token_for(user_id: str, session_id: str, now: datetime) -> str:
        return mint_access_token(user_id=user_id, session_id=session_id, expires_at=now + ACCESS_TOKEN_LIFETIME)
