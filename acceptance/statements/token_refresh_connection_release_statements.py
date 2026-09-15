import secrets
from dataclasses import dataclass
from time import perf_counter

from clients.application.auth_client import AuthClient
from clients.application.dto.auth.session_dto import SessionDto

from statements.auth_statements import AuthStatements
from statements.pool_release_assertions import (
    REQUESTS_PER_OUTCOME,
    PoolAttempt,
    assert_answered_without_waiting_for_a_connection,
)
from statements.session_refresh_statements import SessionRefreshStatements
from statements.wire_contract import HTTP_OK, HTTP_UNAUTHORIZED

SUCCESSFUL_REFRESH = "successful refresh"
CONSUMED_TOKEN_REFRESH = "consumed-token refresh"
UNKNOWN_TOKEN_REFRESH = "unknown-token refresh"

UNKNOWN_TOKEN_BYTES = 48


@dataclass(frozen=True)
class RefreshOutcome:
    name: str
    expected_status: int


@dataclass(frozen=True)
class SessionAfterRotations:
    session: SessionDto
    rotated: SessionDto
    seconds: float


class TokenRefreshConnectionReleaseStatements:
    def __init__(
        self,
        auth_client: AuthClient,
        auth_statements: AuthStatements,
        session_refresh_statements: SessionRefreshStatements,
    ):
        self.auth_client = auth_client
        self.auth_statements = auth_statements
        self.session_refresh_statements = session_refresh_statements
        self._session: SessionDto | None = None
        self._consumed_token: str | None = None

    async def given_live_session_and_every_refresh_outcome(self) -> list[RefreshOutcome]:
        self._session = await self.auth_statements.given_live_session()
        return [
            RefreshOutcome(name=SUCCESSFUL_REFRESH, expected_status=HTTP_OK),
            RefreshOutcome(name=CONSUMED_TOKEN_REFRESH, expected_status=HTTP_UNAUTHORIZED),
            RefreshOutcome(name=UNKNOWN_TOKEN_REFRESH, expected_status=HTTP_UNAUTHORIZED),
        ]

    async def repeat_each_outcome_past_pool_capacity(self, outcomes: list[RefreshOutcome]) -> list[PoolAttempt]:
        return [await self._attempt(outcome) for _ in range(REQUESTS_PER_OUTCOME) for outcome in outcomes]

    async def refresh_once_more_after_every_repetition(self) -> SessionAfterRotations:
        session = self._require_live_session()
        started = perf_counter()
        rotated = await self.auth_client.refresh_session(session.refresh_token)
        return SessionAfterRotations(session=session, rotated=rotated, seconds=perf_counter() - started)

    def assert_session_still_rotates_without_waiting(self, after: SessionAfterRotations) -> None:
        self.session_refresh_statements.assert_rotation_succeeded(after.rotated)
        self.session_refresh_statements.assert_session_identifier_is_unchanged(after.session, after.rotated)
        self.session_refresh_statements.assert_both_tokens_are_new(after.session, after.rotated)
        assert_answered_without_waiting_for_a_connection(after.seconds, "the refresh after every repetition")

    async def _attempt(self, outcome: RefreshOutcome) -> PoolAttempt:
        token = self._token_for(outcome)
        started = perf_counter()
        answered = await self.auth_client.refresh_session(token)
        seconds = perf_counter() - started
        self._remember_rotation(outcome, token, answered)
        return PoolAttempt(
            outcome_name=outcome.name,
            expected_status=outcome.expected_status,
            http_status=answered.http_status,
            seconds=seconds,
        )

    def _token_for(self, outcome: RefreshOutcome) -> str:
        if outcome.name == SUCCESSFUL_REFRESH:
            return self._require_live_session().refresh_token
        if outcome.name == CONSUMED_TOKEN_REFRESH:
            assert self._consumed_token is not None, (
                "a successful refresh must consume a token before the consumed-token outcome is driven"
            )
            return self._consumed_token
        return secrets.token_urlsafe(UNKNOWN_TOKEN_BYTES)

    def _remember_rotation(self, outcome: RefreshOutcome, presented: str, answered: SessionDto) -> None:
        if outcome.name != SUCCESSFUL_REFRESH or answered.http_status != HTTP_OK:
            return
        self._consumed_token = presented
        self._session = answered

    def _require_live_session(self) -> SessionDto:
        assert self._session is not None and self._session.refresh_token, (
            "a live session must be issued before a refresh outcome is driven"
        )
        return self._session
