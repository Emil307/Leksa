import json
from dataclasses import dataclass
from typing import Any

from clients.application.auth_client import CHALLENGE_VERIFY_PATH, AuthClient
from httpx import Response
from redis.asyncio import Redis

from statements.auth_statements import HTTP_OK, AuthStatements, RequestedCode, is_canonical_uuid
from statements.challenge_resend_statements import RECORD_KEY, redis_settings
from statements.outbox_database import OutboxDatabase

HTTP_UNAUTHORIZED = 401
UNAUTHORIZED = "UNAUTHORIZED"
ERROR_ENVELOPE_FIELDS = frozenset({"code", "message", "payload"})
SESSION_BEARING_NAMES = ("session", "user", "accessToken", "refreshToken", "token")
DIGIT_SHIFT = 1
DECIMAL_BASE = 10
SPENT_BY_ONE_ATTEMPT = 1

FOREIGN = "чужой живой challenge"
OWN = "собственный живой challenge с неверным кодом"


def _shifted(code: str) -> str:
    shifted = "".join(str((int(digit) + DIGIT_SHIFT) % DECIMAL_BASE) for digit in code)
    assert shifted != code, f"the wrong code must differ from the working code {code!r}"
    return shifted


@dataclass(frozen=True)
class TwoUsers:
    first: RequestedCode
    second: RequestedCode


@dataclass(frozen=True)
class VerifyAnswer:
    label: str
    http_status: int
    body: dict[str, Any]
    raw_text: str


class ForeignChallengeIdStatements:
    def __init__(
        self,
        auth_client: AuthClient,
        auth_statements: AuthStatements,
        outbox_database: OutboxDatabase,
    ):
        self.auth_client = auth_client
        self.auth_statements = auth_statements
        self.outbox_database = outbox_database

    async def given_two_users_each_holding_their_own_code(self) -> TwoUsers:
        first = await self._requested_code()
        second = await self._requested_code()
        assert first.challenge_id != second.challenge_id, (
            f"the two users must hold two different challenge identifiers, both answered {first.challenge_id!r}"
        )
        assert first.code != second.code, (
            f"the scenario needs two distinguishable codes, both users received {first.code!r}"
        )
        return TwoUsers(first=first, second=second)

    async def attempts_of_the_first_challenge(self, users: TwoUsers) -> int:
        return await self._attempts_of(users.first.challenge_id)

    async def the_first_user_presents_the_challenge_id_of_the_second(self, users: TwoUsers) -> VerifyAnswer:
        return await self._verify(FOREIGN, users.second.challenge_id, users.first.code)

    async def the_first_user_presents_a_wrong_code_on_their_own_challenge(self, users: TwoUsers) -> VerifyAnswer:
        return await self._verify(OWN, users.first.challenge_id, _shifted(users.first.code))

    def assert_rejected_as_failed_authorization(self, answer: VerifyAnswer) -> None:
        assert answer.http_status == HTTP_UNAUTHORIZED, (
            f"«{answer.label}» must be refused with {HTTP_UNAUTHORIZED}, "
            f"got {answer.http_status} with body {answer.raw_text!r}"
        )
        assert answer.body.get("code") == UNAUTHORIZED, (
            f"«{answer.label}» must answer error code {UNAUTHORIZED}, got {answer.body.get('code')!r}"
        )
        assert frozenset(answer.body) == ERROR_ENVELOPE_FIELDS, (
            f"«{answer.label}» must answer exactly {sorted(ERROR_ENVELOPE_FIELDS)}, got {sorted(answer.body)}"
        )
        assert answer.body.get("message"), f"«{answer.label}» must carry a message, got {answer.body.get('message')!r}"

    def assert_carries_no_session_and_no_token(self, answer: VerifyAnswer) -> None:
        leaked = [name for name in SESSION_BEARING_NAMES if name in answer.raw_text]
        assert not leaked, (
            f"«{answer.label}» must issue no session and no token to anybody, found {leaked!r} in {answer.raw_text!r}"
        )

    def assert_indistinguishable_from_a_wrong_code_on_the_own_challenge(
        self, foreign: VerifyAnswer, own: VerifyAnswer
    ) -> None:
        assert foreign.http_status == own.http_status, (
            f"«{FOREIGN}» answered {foreign.http_status} while «{OWN}» answered {own.http_status} — "
            "the status alone tells a foreign live challenge from an own one"
        )
        assert foreign.body.get("code") == own.body.get("code"), (
            f"the error code must not tell the two apart: «{FOREIGN}» answered {foreign.body.get('code')!r}, "
            f"«{OWN}» answered {own.body.get('code')!r}"
        )
        assert foreign.body.get("message") == own.body.get("message"), (
            f"the message must not tell the two apart: «{FOREIGN}» answered {foreign.body.get('message')!r}, "
            f"«{OWN}» answered {own.body.get('message')!r}"
        )
        assert foreign.body == own.body, (
            f"both bodies must be identical, «{FOREIGN}» answered {foreign.body!r} while «{OWN}» answered {own.body!r}"
        )

    async def assert_the_attempts_of_the_first_challenge_are_untouched(self, users: TwoUsers, before: int) -> None:
        after = await self._attempts_of(users.first.challenge_id)
        assert after == before, (
            f"presenting a foreign challenge identifier must spend no attempt of the first user — "
            f"the counter of {users.first.challenge_id!r} moved from {before} to {after}"
        )

    async def assert_a_wrong_code_on_the_own_challenge_does_spend_one(self, users: TwoUsers, before: int) -> None:
        after = await self._attempts_of(users.first.challenge_id)
        assert after == before + SPENT_BY_ONE_ATTEMPT, (
            f"a wrong code on the own challenge must spend exactly one attempt — the counter of "
            f"{users.first.challenge_id!r} moved from {before} to {after}"
        )

    async def assert_the_second_user_code_still_issues_a_session(self, users: TwoUsers) -> None:
        session = await self.auth_client.verify_challenge(users.second.challenge_id, users.second.code)
        assert session.http_status == HTTP_OK, (
            f"the correct code of the second user must still be accepted with {HTTP_OK}, got {session.http_status}"
        )
        assert is_canonical_uuid(session.session_id), (
            f"the second user must receive a canonical session id, got {session.session_id!r}"
        )
        assert is_canonical_uuid(session.user_id), (
            f"the second user must receive a canonical user id, got {session.user_id!r}"
        )
        assert session.refresh_token, "the second user must receive a refresh token"
        assert session.access_token, "the second user must receive an access token"

    async def _requested_code(self) -> RequestedCode:
        email = self.auth_statements.new_user_email()
        return await self.auth_statements.request_code_and_capture(email)

    async def _verify(self, label: str, challenge_id: str, code: str) -> VerifyAnswer:
        response = await self.auth_client.post(CHALLENGE_VERIFY_PATH, json={"challengeId": challenge_id, "code": code})
        return VerifyAnswer(
            label=label,
            http_status=response.status_code,
            body=self._body_of(response),
            raw_text=response.text,
        )

    async def _attempts_of(self, challenge_id: str) -> int:
        key = RECORD_KEY.format(challenge_id=challenge_id)
        client = Redis(**redis_settings())
        try:
            record = await client.get(key)
            assert record is not None, f"the live challenge must still be stored under {key!r}"
            return int(json.loads(record)["attempts"])
        finally:
            await client.aclose()

    @staticmethod
    def _body_of(response: Response) -> dict[str, Any]:
        try:
            body = response.json()
        except ValueError:
            return {}
        return body if isinstance(body, dict) else {}
