import asyncio

from clients.application.dto.auth.challenge_dto import ChallengeStartDto
from redis.asyncio import Redis

from statements.auth_statements import EMAIL_CODE, AuthStatements
from statements.challenge_start_cooldown_statements import (
    RETRY_AFTER_KEY,
    ChallengeStartCooldownStatements,
    CooldownDenial,
)
from statements.environment import required_setting

COOLDOWN_KEY = "challenge:cooldown:{challenge_type}:{uniqueness_key}"
REDIS_HOST_VARIABLE = "REDIS_HOST"
REDIS_PORT_VARIABLE = "REDIS_PORT"
REDIS_PASSWORD_VARIABLE = "REDIS_PASSWORD"

KEY_HELD = 1
NO_KEY_LEFT = 0


class CooldownBoundaryStatements:
    def __init__(
        self,
        auth_statements: AuthStatements,
        cooldown_statements: ChallengeStartCooldownStatements,
    ):
        self.auth_statements = auth_statements
        self.cooldown_statements = cooldown_statements

    async def given_user_just_requested_a_code(self) -> str:
        email = self.auth_statements.new_user_email()
        challenge = await self.auth_statements.request_code(email)
        self.auth_statements.assert_challenge_accepted(challenge)
        await self.assert_cooldown_is_armed(email)
        return email

    async def given_cooldown_has_milliseconds_left(self, email: str, milliseconds: int) -> None:
        client = self._client()
        try:
            reshaped = await client.pexpire(self._cooldown_key(email), milliseconds)
        finally:
            await client.aclose()
        assert reshaped == KEY_HELD, (
            f"the cooldown of {email} must still be armed to be moved {milliseconds}ms from its end, "
            f"redis answered {reshaped}"
        )

    async def given_cooldown_has_just_ended(self, email: str) -> None:
        client = self._client()
        try:
            released = await client.delete(self._cooldown_key(email))
        finally:
            await client.aclose()
        assert released == KEY_HELD, (
            f"the cooldown of {email} must be armed before it can be brought to its end, redis answered {released}"
        )

    async def given_a_moment_has_passed_since_the_cooldown_ended(self, email: str, seconds: float) -> None:
        await self.given_cooldown_has_just_ended(email)
        await asyncio.sleep(seconds)

    async def request_code_again(self, email: str) -> CooldownDenial:
        return await self.cooldown_statements.request_code_again(email)

    async def request_code_again_expecting_acceptance(self, email: str) -> ChallengeStartDto:
        return await self.auth_statements.request_code(email)

    def assert_rejected_by_cooldown_with_remaining_wait(self, denial: CooldownDenial, expected: int) -> None:
        self.cooldown_statements.assert_rejected_by_cooldown(denial)
        self.cooldown_statements.assert_carries_remaining_wait_in_whole_seconds(denial)
        remaining = denial.payload[RETRY_AFTER_KEY]
        assert remaining == expected, (
            f"{RETRY_AFTER_KEY} must be exactly {expected} whole seconds — a client that waits it out "
            f"must not be refused again — got {remaining}"
        )

    def assert_request_accepted(self, challenge: ChallengeStartDto) -> None:
        self.auth_statements.assert_challenge_carries_identifier_and_type(challenge)

    async def assert_cooldown_is_armed(self, email: str) -> None:
        held = await self._key_count(email)
        assert held == KEY_HELD, f"the cooldown key of {email} must be armed after a code request, found {held}"

    async def assert_cooldown_has_lapsed(self, email: str) -> None:
        held = await self._key_count(email)
        assert held == NO_KEY_LEFT, f"the cooldown key of {email} must be gone once its end is reached, found {held}"

    async def _key_count(self, email: str) -> int:
        client = self._client()
        try:
            return await client.exists(self._cooldown_key(email))
        finally:
            await client.aclose()

    def _cooldown_key(self, email: str) -> str:
        return COOLDOWN_KEY.format(challenge_type=EMAIL_CODE, uniqueness_key=email)

    def _client(self) -> Redis:
        return Redis(
            host=required_setting(REDIS_HOST_VARIABLE),
            port=int(required_setting(REDIS_PORT_VARIABLE)),
            password=required_setting(REDIS_PASSWORD_VARIABLE),
        )
