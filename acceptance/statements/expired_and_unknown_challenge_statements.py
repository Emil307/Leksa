import asyncio
import os
import uuid
from dataclasses import dataclass
from typing import Any

import redis.asyncio as redis
from clients.application.auth_client import AuthClient
from httpx import Response

from statements.auth_statements import AuthStatements
from statements.environment import required_setting
from statements.outbox_database import OutboxDatabase

VERIFY_PATH = "/api/v1/auth/challenge/verify"
HTTP_UNAUTHORIZED = 401
UNAUTHORIZED = "UNAUTHORIZED"
ERROR_ENVELOPE_FIELDS = frozenset({"code", "message", "payload"})
SESSION_BEARING_NAMES = ("session", "user", "accessToken", "refreshToken", "token")

CHALLENGE_RECORD_KEY = "challenge:{challenge_id}"
EXPIRY_MILLISECONDS = 1
EXPIRY_POLL_ATTEMPTS = 100
EXPIRY_POLL_SECONDS = 0.05

DEFAULT_REDIS_DB = "0"

EXPIRED = "истёкший challenge"
UNKNOWN = "никогда не существовавший challenge"


def redis_settings() -> dict[str, Any]:
    return {
        "host": required_setting("REDIS_HOST"),
        "port": int(required_setting("REDIS_PORT")),
        "password": os.environ.get("REDIS_PASSWORD") or None,
        "db": int(os.environ.get("REDIS_DB", DEFAULT_REDIS_DB)),
    }


@dataclass(frozen=True)
class VerifiedAnswer:
    label: str
    http_status: int
    body: dict[str, Any]
    raw_text: str


@dataclass(frozen=True)
class ExpiredAndUnknownChallenges:
    expired_challenge_id: str
    unknown_challenge_id: str
    code: str


class ExpiredAndUnknownChallengeStatements:
    def __init__(
        self,
        auth_client: AuthClient,
        auth_statements: AuthStatements,
        outbox_database: OutboxDatabase,
    ):
        self.auth_client = auth_client
        self.auth_statements = auth_statements
        self.outbox_database = outbox_database

    async def given_an_expired_challenge_and_an_unknown_identifier(
        self,
    ) -> ExpiredAndUnknownChallenges:
        email = self.auth_statements.new_user_email()
        requested = await self.auth_statements.request_code_and_capture(email)

        await self._expire(requested.challenge_id)

        unknown_challenge_id = str(uuid.uuid4())
        assert unknown_challenge_id != requested.challenge_id, (
            "the never-issued identifier must differ from the expired one"
        )

        return ExpiredAndUnknownChallenges(
            expired_challenge_id=requested.challenge_id,
            unknown_challenge_id=unknown_challenge_id,
            code=requested.code,
        )

    async def verify_each(self, challenges: ExpiredAndUnknownChallenges) -> tuple[VerifiedAnswer, VerifiedAnswer]:
        expired = await self._verify(EXPIRED, challenges.expired_challenge_id, challenges.code)
        unknown = await self._verify(UNKNOWN, challenges.unknown_challenge_id, challenges.code)
        return expired, unknown

    def assert_both_were_refused_as_unauthorized(self, answers: tuple[VerifiedAnswer, VerifiedAnswer]) -> None:
        for answer in answers:
            assert answer.http_status == HTTP_UNAUTHORIZED, (
                f"«{answer.label}» must be refused with {HTTP_UNAUTHORIZED}, "
                f"got {answer.http_status} with body {answer.raw_text!r}"
            )
            assert frozenset(answer.body) == ERROR_ENVELOPE_FIELDS, (
                f"«{answer.label}» must answer exactly {sorted(ERROR_ENVELOPE_FIELDS)}, got {sorted(answer.body)}"
            )
            assert answer.body.get("code") == UNAUTHORIZED, (
                f"«{answer.label}» must answer error code {UNAUTHORIZED}, got {answer.body.get('code')!r}"
            )
            assert answer.body.get("message"), (
                f"«{answer.label}» must carry a message, got {answer.body.get('message')!r}"
            )

    def assert_the_two_answers_are_indistinguishable(self, answers: tuple[VerifiedAnswer, VerifiedAnswer]) -> None:
        expired, unknown = answers
        assert expired.http_status == unknown.http_status, (
            f"«{EXPIRED}» answered {expired.http_status} while «{UNKNOWN}» answered "
            f"{unknown.http_status} — the status alone tells whether the challenge existed"
        )
        assert expired.body.get("code") == unknown.body.get("code"), (
            f"the error code must not tell the two apart: «{EXPIRED}» answered "
            f"{expired.body.get('code')!r}, «{UNKNOWN}» answered {unknown.body.get('code')!r}"
        )
        assert expired.body.get("message") == unknown.body.get("message"), (
            f"the message must not tell the two apart: «{EXPIRED}» answered "
            f"{expired.body.get('message')!r}, «{UNKNOWN}» answered {unknown.body.get('message')!r}"
        )
        assert expired.body == unknown.body, (
            f"both bodies must be identical, «{EXPIRED}» answered {expired.body!r} "
            f"while «{UNKNOWN}» answered {unknown.body!r}"
        )

    def assert_neither_answer_carries_a_session_or_a_token(
        self, answers: tuple[VerifiedAnswer, VerifiedAnswer]
    ) -> None:
        for answer in answers:
            leaked = [name for name in SESSION_BEARING_NAMES if name in answer.raw_text]
            assert not leaked, (
                f"«{answer.label}» must carry neither a session nor a token, found {leaked!r} in {answer.raw_text!r}"
            )

    async def _verify(self, label: str, challenge_id: str, code: str) -> VerifiedAnswer:
        response = await self.auth_client.post(VERIFY_PATH, json={"challengeId": challenge_id, "code": code})
        return VerifiedAnswer(
            label=label,
            http_status=response.status_code,
            body=self._body_of(response),
            raw_text=response.text,
        )

    async def _expire(self, challenge_id: str) -> None:
        key = CHALLENGE_RECORD_KEY.format(challenge_id=challenge_id)
        client = redis.Redis(**redis_settings())
        try:
            shortened = await client.pexpire(key, EXPIRY_MILLISECONDS)
            assert int(shortened) == 1, f"the started challenge must be stored under {key!r} before it expires"
            for _ in range(EXPIRY_POLL_ATTEMPTS):
                if int(await client.exists(key)) == 0:
                    return
                await asyncio.sleep(EXPIRY_POLL_SECONDS)
            raise AssertionError(f"{key!r} must fall out of the store once its lifetime is spent")
        finally:
            await client.aclose()

    @staticmethod
    def _body_of(response: Response) -> dict[str, Any]:
        try:
            body = response.json()
        except ValueError:
            return {}
        return body if isinstance(body, dict) else {}
