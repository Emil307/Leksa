import os
from dataclasses import dataclass

import asyncpg
from clients.application.auth_client import AuthClient
from clients.application.dto.auth.challenge_dto import ChallengeStartDto
from redis.asyncio import Redis

from statements.auth_database import connection_settings
from statements.auth_statements import EMAIL_CODE, AuthStatements, is_canonical_uuid
from statements.environment import required_setting
from statements.outbox_database import OutboxDatabase

HTTP_UNAUTHORIZED = 401
EXPECTED_QUEUED_REQUESTS = 2

COOLDOWN_KEY = "challenge:cooldown:{challenge_type}:{uniqueness_key}"
POINTER_KEY = "challenge:key:{challenge_type}:{uniqueness_key}"
RECORD_KEY = "challenge:{challenge_id}"

QUEUED_EMAIL_CODES = """
SELECT data->'variables'->>'code' AS code
FROM notifications.t_outbox
WHERE type = 'EMAIL' AND data->>'to' = $1
ORDER BY created_at
"""


def redis_settings() -> dict[str, object]:
    return {
        "host": required_setting("REDIS_HOST"),
        "port": int(required_setting("REDIS_PORT")),
        "password": os.environ.get("REDIS_PASSWORD") or None,
        "db": int(os.environ.get("REDIS_DB", "0")),
        "decode_responses": True,
    }


@dataclass(frozen=True)
class IssuedChallenge:
    email: str
    challenge: ChallengeStartDto
    code: str


class ChallengeResendStatements:
    def __init__(
        self,
        auth_client: AuthClient,
        auth_statements: AuthStatements,
        outbox_database: OutboxDatabase,
    ):
        self.auth_client = auth_client
        self.auth_statements = auth_statements
        self.outbox_database = outbox_database

    async def given_requested_code_whose_cooldown_expired(self) -> IssuedChallenge:
        email = self.auth_statements.new_user_email()
        issued = await self._request_code(email)
        await self._expire_cooldown(email)
        return issued

    async def request_code_again(self, issued: IssuedChallenge) -> ChallengeStartDto:
        return await self.auth_statements.request_code(issued.email)

    def assert_challenge_is_new_with_a_new_expiry(self, reissued: ChallengeStartDto, issued: IssuedChallenge) -> None:
        self.auth_statements.assert_challenge_carries_identifier_and_type(reissued)
        assert reissued.challenge_id != issued.challenge.challenge_id, (
            f"the repeated request must answer with a new challengeId, it reused {issued.challenge.challenge_id!r}"
        )
        assert issued.challenge.expires_at is not None and reissued.expires_at is not None, (
            "both challenges must carry an expiresAt instant"
        )
        assert reissued.expires_at > issued.challenge.expires_at, (
            f"the repeated request must answer with a later expiresAt than "
            f"{issued.challenge.expires_at.isoformat()}, got {reissued.expires_at.isoformat()}"
        )
        self.auth_statements.assert_expiry_is_creation_plus_configured_code_lifetime(reissued)

    async def assert_second_request_is_queued_with_a_new_code(self, issued: IssuedChallenge) -> None:
        codes = await self._queued_codes_for(issued.email)
        assert len(codes) == EXPECTED_QUEUED_REQUESTS, (
            f"{issued.email} must own exactly {EXPECTED_QUEUED_REQUESTS} queued email requests, found {codes!r}"
        )
        assert codes[0] == issued.code, (
            f"the first queued request must still carry the original code {issued.code!r}, got {codes[0]!r}"
        )
        assert codes[1] != issued.code, f"the second queued request must carry a new code, it repeated {issued.code!r}"

    async def assert_previous_code_no_longer_issues_a_session(self, issued: IssuedChallenge) -> None:
        rejected = await self.auth_client.verify_challenge(issued.challenge.challenge_id, issued.code)
        assert rejected.http_status == HTTP_UNAUTHORIZED, (
            f"the superseded code must be rejected with {HTTP_UNAUTHORIZED}, got {rejected.http_status}"
        )
        assert rejected.session_id is None, f"no session may be issued, got {rejected.session_id!r}"
        assert rejected.refresh_token is None, f"no refresh token may be issued, got {rejected.refresh_token!r}"
        assert rejected.access_token is None, f"no access token may be issued, got {rejected.access_token!r}"

    async def assert_email_keeps_exactly_one_live_challenge(
        self, reissued: ChallengeStartDto, issued: IssuedChallenge
    ) -> None:
        candidates = [issued.challenge.challenge_id, reissued.challenge_id]
        redis = Redis(**redis_settings())
        try:
            pointer = await redis.get(self._pointer_key(issued.email))
            live = [candidate for candidate in candidates if await redis.ttl(self._record_key(candidate)) > 0]
        finally:
            await redis.aclose()
        assert live == [reissued.challenge_id], (
            f"{issued.email} must keep exactly the new challenge {reissued.challenge_id!r} alive, found {live!r}"
        )
        assert pointer == reissued.challenge_id, (
            f"the live challenge of {issued.email} must be {reissued.challenge_id!r}, the pointer holds {pointer!r}"
        )

    async def _request_code(self, email: str) -> IssuedChallenge:
        challenge = await self.auth_statements.request_code(email)
        self.auth_statements.assert_challenge_accepted(challenge)
        code = await self.outbox_database.queued_code_for(email)
        assert code is not None, f"a login code must be queued for {email}, the outbox stayed empty"
        assert is_canonical_uuid(challenge.challenge_id), (
            f"the started challenge must carry a canonical UUID id, got {challenge.challenge_id!r}"
        )
        return IssuedChallenge(email=email, challenge=challenge, code=code)

    async def _expire_cooldown(self, email: str) -> None:
        redis = Redis(**redis_settings())
        try:
            removed = await redis.delete(COOLDOWN_KEY.format(challenge_type=EMAIL_CODE, uniqueness_key=email))
        finally:
            await redis.aclose()
        assert removed == 1, (
            f"the resend cooldown of {email} must have been armed by the first request — "
            f"expiring it removed {removed} keys"
        )

    async def _queued_codes_for(self, email: str) -> list[str]:
        connection = await asyncpg.connect(**connection_settings())
        try:
            rows = await connection.fetch(QUEUED_EMAIL_CODES, email)
        finally:
            await connection.close()
        return [row["code"] for row in rows]

    @staticmethod
    def _pointer_key(email: str) -> str:
        return POINTER_KEY.format(challenge_type=EMAIL_CODE, uniqueness_key=email)

    @staticmethod
    def _record_key(challenge_id: str) -> str:
        return RECORD_KEY.format(challenge_id=challenge_id)
