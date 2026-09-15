import asyncio
from dataclasses import dataclass
from typing import Any

from clients.application.auth_client import CHALLENGE_VERIFY_PATH, AuthClient
from httpx import Response

from statements.auth_database import AuthDatabase
from statements.auth_statements import HTTP_OK, assert_exactly_one_session, is_canonical_uuid
from statements.challenge_verify_statements import ChallengeVerifyStatements, RegisteredUserWithCode

CONCURRENT_CALLS = 2
MISSING_CHALLENGE_MARKERS = ("not found", "does not exist", "no such challenge", "unknown challenge")


@dataclass(frozen=True)
class VerifyOutcome:
    http_status: int
    user_id: str | None
    session_id: str | None
    body: str


class ConcurrentVerifyStatements:
    def __init__(
        self,
        auth_client: AuthClient,
        challenge_verify_statements: ChallengeVerifyStatements,
        auth_database: AuthDatabase,
    ):
        self.auth_client = auth_client
        self.challenge_verify_statements = challenge_verify_statements
        self.auth_database = auth_database

    async def given_a_user_holding_a_working_code(self) -> RegisteredUserWithCode:
        return await self.challenge_verify_statements.given_registered_user_holding_a_valid_code()

    async def release_two_verifications_of_the_same_code_together(
        self, registered: RegisteredUserWithCode
    ) -> list[VerifyOutcome]:
        released = [self._verify(registered) for _ in range(CONCURRENT_CALLS)]
        return list(await asyncio.gather(*released))

    def assert_both_answers_are_successful_and_carry_the_same_session(
        self, outcomes: list[VerifyOutcome], registered: RegisteredUserWithCode
    ) -> None:
        statuses = [outcome.http_status for outcome in outcomes]
        assert statuses == [HTTP_OK] * CONCURRENT_CALLS, (
            f"both simultaneous verifications of challenge {registered.challenge_id} must be accepted "
            f"with {HTTP_OK}, got {statuses} — bodies {[outcome.body for outcome in outcomes]}"
        )

        session_ids = [outcome.session_id for outcome in outcomes]
        for session_id in session_ids:
            assert is_canonical_uuid(session_id), (
                f"every simultaneous verification must answer with a canonical UUID session id, got {session_id!r}"
            )
        assert len(set(session_ids)) == 1, (
            f"both simultaneous verifications must answer with one and the same session id, got {session_ids!r}"
        )

        user_ids = [outcome.user_id for outcome in outcomes]
        assert user_ids == [registered.user_id] * CONCURRENT_CALLS, (
            f"both simultaneous verifications must answer with the existing user {registered.user_id!r}, "
            f"got {user_ids!r}"
        )

    async def assert_exactly_one_session_is_stored(
        self, outcomes: list[VerifyOutcome], registered: RegisteredUserWithCode
    ) -> None:
        stored = await self.auth_database.session_ids_of_user(registered.user_id)
        assert_exactly_one_session(stored, outcomes[0].session_id, "two simultaneous verifications of one code")

    def assert_no_answer_refuses_the_challenge_as_missing(self, outcomes: list[VerifyOutcome]) -> None:
        for outcome in outcomes:
            lowered = outcome.body.lower()
            refusals = [marker for marker in MISSING_CHALLENGE_MARKERS if marker in lowered]
            assert not refusals, (
                f"the losing simultaneous verification must not be refused as a missing challenge, "
                f"the answer {outcome.http_status} carried {refusals!r} in {outcome.body!r}"
            )

    async def _verify(self, registered: RegisteredUserWithCode) -> VerifyOutcome:
        payload = {"challengeId": registered.challenge_id, "code": registered.code}
        response = await self.auth_client.post(CHALLENGE_VERIFY_PATH, json=payload)
        return self._outcome_of(response)

    def _outcome_of(self, response: Response) -> VerifyOutcome:
        body = self._json_object(response)
        session = body.get("session") if isinstance(body.get("session"), dict) else {}
        user = body.get("user") if isinstance(body.get("user"), dict) else {}
        return VerifyOutcome(
            http_status=response.status_code,
            user_id=user.get("id"),
            session_id=session.get("id"),
            body=response.text,
        )

    @staticmethod
    def _json_object(response: Response) -> dict[str, Any]:
        try:
            body = response.json()
        except ValueError:
            return {}
        return body if isinstance(body, dict) else {}
