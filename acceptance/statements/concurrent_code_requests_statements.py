import asyncio
from dataclasses import dataclass
from typing import Any

from clients.application.auth_client import CHALLENGE_START_PATH, AuthClient
from clients.application.dto.auth.session_dto import SessionDto
from httpx import AsyncClient

from statements.auth_statements import EMAIL_CODE, AuthStatements, RequestedCode, is_canonical_uuid
from statements.challenge_start_cooldown_statements import ChallengeStartCooldownStatements, CooldownDenial
from statements.outbox_database import OutboxDatabase

HTTP_OK = 200
CONCURRENT_REQUESTS = 2
SINGLE_WINNER = 1
SINGLE_LOSER = 1


@dataclass(frozen=True)
class CodeRequestOutcome:
    http_status: int
    challenge_id: str | None
    code: str | None
    payload: dict[str, Any]

    def as_cooldown_denial(self) -> CooldownDenial:
        return CooldownDenial(http_status=self.http_status, code=self.code, payload=self.payload)


@dataclass(frozen=True)
class RaceOutcome:
    outcomes: tuple[CodeRequestOutcome, ...]

    @property
    def winners(self) -> list[CodeRequestOutcome]:
        return [outcome for outcome in self.outcomes if outcome.http_status == HTTP_OK]

    @property
    def losers(self) -> list[CodeRequestOutcome]:
        return [outcome for outcome in self.outcomes if outcome.http_status != HTTP_OK]

    def statuses(self) -> list[int]:
        return [outcome.http_status for outcome in self.outcomes]


class ConcurrentCodeRequestsStatements:
    def __init__(
        self,
        http_client: AsyncClient,
        auth_statements: AuthStatements,
        cooldown_statements: ChallengeStartCooldownStatements,
        outbox_database: OutboxDatabase,
        auth_client: AuthClient,
    ):
        self.http_client = http_client
        self.auth_statements = auth_statements
        self.cooldown_statements = cooldown_statements
        self.outbox_database = outbox_database
        self.auth_client = auth_client

    def given_no_live_challenge_for_this_email(self) -> str:
        return self.auth_statements.new_user_email()

    async def release_two_code_requests_together(self, email: str) -> RaceOutcome:
        released = asyncio.Event()
        outcomes = await asyncio.gather(
            *(self._request_code_on_release(email, released) for _ in range(CONCURRENT_REQUESTS)),
            self._release(released),
        )
        return RaceOutcome(outcomes=tuple(outcomes[:CONCURRENT_REQUESTS]))

    def assert_exactly_one_created_a_challenge(self, race: RaceOutcome) -> None:
        winners = race.winners
        assert len(winners) == SINGLE_WINNER, (
            f"exactly {SINGLE_WINNER} of the two simultaneous code requests must create a challenge, "
            f"got statuses {race.statuses()}"
        )
        assert is_canonical_uuid(winners[0].challenge_id), (
            f"the winning request must answer a canonical UUID challengeId, got {winners[0].challenge_id!r}"
        )

    def assert_loser_refused_by_cooldown(self, race: RaceOutcome) -> None:
        losers = race.losers
        assert len(losers) == SINGLE_LOSER, (
            f"exactly {SINGLE_LOSER} of the two simultaneous code requests must be refused, "
            f"got statuses {race.statuses()}"
        )
        denial = losers[0].as_cooldown_denial()
        self.cooldown_statements.assert_rejected_by_cooldown(denial)
        self.cooldown_statements.assert_carries_remaining_wait_in_whole_seconds(denial)

    async def assert_single_queued_request(self, email: str) -> None:
        await self.cooldown_statements.assert_single_queued_request(email)

    async def assert_winner_holds_the_only_live_challenge(self, race: RaceOutcome, email: str) -> SessionDto:
        code = await self.outbox_database.queued_code_for(email)
        assert code is not None, f"a login code must be queued for {email}, the outbox stayed empty"
        requested = RequestedCode(challenge_id=race.winners[0].challenge_id, code=code)
        return await self.cooldown_statements.assert_earlier_code_still_issues_a_session(requested)

    async def _release(self, released: asyncio.Event) -> None:
        await asyncio.sleep(0)
        released.set()

    async def _request_code_on_release(self, email: str, released: asyncio.Event) -> CodeRequestOutcome:
        await released.wait()
        response = await self.http_client.post(CHALLENGE_START_PATH, json={"email": email, "challengeType": EMAIL_CODE})
        body = response.json() if response.content else {}
        body = body if isinstance(body, dict) else {}
        payload = body.get("payload")
        return CodeRequestOutcome(
            http_status=response.status_code,
            challenge_id=body.get("challengeId"),
            code=body.get("code"),
            payload=payload if isinstance(payload, dict) else {},
        )
