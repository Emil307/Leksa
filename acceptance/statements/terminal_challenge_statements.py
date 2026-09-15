import uuid
from dataclasses import dataclass

from clients.application.auth_client import AuthClient
from clients.application.dto.auth.session_dto import SessionDto
from redis.asyncio import Redis

from statements.auth_database import AuthDatabase
from statements.auth_statements import EMAIL_CODE, AuthStatements
from statements.challenge_resend_statements import COOLDOWN_KEY, POINTER_KEY, RECORD_KEY, redis_settings
from statements.outbox_database import OutboxDatabase

HTTP_UNAUTHORIZED = 401
VERIFICATION_KEY = "challenge:verified:{challenge_id}"
ABSENT_KEY_TTL = -2
WRONG_CODE = "000000"
ALTERNATE_WRONG_CODE = "111111"
ATTEMPT_GUARD = 20
NEVER_EXISTED_CODE = "123456"


@dataclass(frozen=True)
class TerminalChallenge:
    state: str
    email: str
    challenge_id: str
    code: str


@dataclass(frozen=True)
class ChallengeTrace:
    key_lifetimes: dict[str, int]
    users_with_email: int


class TerminalChallengeStatements:
    def __init__(
        self,
        auth_client: AuthClient,
        auth_statements: AuthStatements,
        auth_database: AuthDatabase,
        outbox_database: OutboxDatabase,
    ):
        self.auth_client = auth_client
        self.auth_statements = auth_statements
        self.auth_database = auth_database
        self.outbox_database = outbox_database

    async def given_challenge_exhausted_by_attempts(self) -> TerminalChallenge:
        issued = await self._issued_challenge("exhausted by attempts")
        wrong = self._wrong_code(issued.code)
        for _ in range(ATTEMPT_GUARD):
            if await self._lifetime_of(RECORD_KEY.format(challenge_id=issued.challenge_id)) == ABSENT_KEY_TTL:
                break
            await self.auth_client.verify_challenge(issued.challenge_id, wrong)
        await self._assert_record_is_gone(issued)
        return issued

    async def given_challenge_whose_code_lifetime_expired(self) -> TerminalChallenge:
        issued = await self._issued_challenge("code lifetime expired")
        await self._drop_keys(
            RECORD_KEY.format(challenge_id=issued.challenge_id),
            POINTER_KEY.format(challenge_type=EMAIL_CODE, uniqueness_key=issued.email),
        )
        await self._assert_record_is_gone(issued)
        return issued

    async def given_challenge_superseded_by_a_new_request(self) -> TerminalChallenge:
        issued = await self._issued_challenge("superseded by a new request")
        await self._drop_keys(COOLDOWN_KEY.format(challenge_type=EMAIL_CODE, uniqueness_key=issued.email))
        reissued = await self.auth_statements.request_code(issued.email)
        self.auth_statements.assert_challenge_accepted(reissued)
        assert reissued.challenge_id != issued.challenge_id, (
            f"the repeated request for {issued.email} must supersede {issued.challenge_id!r} with a new challenge"
        )
        await self._assert_record_is_gone(issued)
        return issued

    async def given_challenge_redeemed_with_an_expired_replay_window(self) -> TerminalChallenge:
        issued = await self._issued_challenge("redeemed, replay window expired")
        redeemed = await self.auth_client.verify_challenge(issued.challenge_id, issued.code)
        self.auth_statements.assert_verify_accepted(redeemed)
        await self._drop_keys(VERIFICATION_KEY.format(challenge_id=issued.challenge_id))
        await self._assert_record_is_gone(issued)
        return issued

    async def given_challenge_that_never_existed(self) -> TerminalChallenge:
        email = self.auth_statements.new_user_email()
        challenge_id = str(uuid.uuid4())
        issued = TerminalChallenge("never existed", email, challenge_id, NEVER_EXISTED_CODE)
        await self._assert_record_is_gone(issued)
        return issued

    async def capture_trace(self, terminal: TerminalChallenge) -> ChallengeTrace:
        lifetimes = {key: await self._lifetime_of(key) for key in self._watched_keys(terminal)}
        return ChallengeTrace(
            key_lifetimes=lifetimes,
            users_with_email=await self.auth_database.count_users_with_email(terminal.email),
        )

    async def verify_code(self, terminal: TerminalChallenge) -> SessionDto:
        return await self.auth_client.verify_challenge(terminal.challenge_id, terminal.code)

    def assert_rejected_as_failed_authorization(self, session: SessionDto, terminal: TerminalChallenge) -> None:
        assert session.http_status == HTTP_UNAUTHORIZED, (
            f"a challenge {terminal.state} must reject the code with {HTTP_UNAUTHORIZED}, got {session.http_status}"
        )

    def assert_no_session_and_no_token_in_the_answer(self, session: SessionDto) -> None:
        assert session.session_id is None, f"no session may be issued, got {session.session_id!r}"
        assert session.refresh_token is None, f"no refresh token may be issued, got {session.refresh_token!r}"
        assert session.access_token is None, f"no access token may be issued, got {session.access_token!r}"

    async def assert_no_user_was_created(self, terminal: TerminalChallenge, before: ChallengeTrace) -> None:
        after = await self.auth_database.count_users_with_email(terminal.email)
        assert after == before.users_with_email, (
            f"the rejected verify must create no user for {terminal.email} — "
            f"the account count moved from {before.users_with_email} to {after}"
        )

    async def assert_challenge_store_kept_no_trace(self, terminal: TerminalChallenge, before: ChallengeTrace) -> None:
        after = await self.capture_trace(terminal)
        self._assert_no_key_was_created_or_removed(terminal, before, after)
        self._assert_no_lifetime_was_reset(terminal, before, after)
        for key in self._keys_that_must_stay_absent(terminal):
            assert after.key_lifetimes[key] == ABSENT_KEY_TTL, (
                f"the rejected verify must leave {key} absent — it now lives {after.key_lifetimes[key]}s"
            )

    def _assert_no_key_was_created_or_removed(
        self, terminal: TerminalChallenge, before: ChallengeTrace, after: ChallengeTrace
    ) -> None:
        live_before = sorted(key for key, ttl in before.key_lifetimes.items() if ttl != ABSENT_KEY_TTL)
        live_after = sorted(key for key, ttl in after.key_lifetimes.items() if ttl != ABSENT_KEY_TTL)
        assert live_after == live_before, (
            f"a challenge {terminal.state} must keep the very same keys — {live_before!r} became {live_after!r}"
        )

    def _assert_no_lifetime_was_reset(
        self, terminal: TerminalChallenge, before: ChallengeTrace, after: ChallengeTrace
    ) -> None:
        extended = {
            key: (before.key_lifetimes[key], ttl)
            for key, ttl in after.key_lifetimes.items()
            if ttl != ABSENT_KEY_TTL and ttl > before.key_lifetimes[key]
        }
        assert not extended, (
            f"a challenge {terminal.state} must have no lifetime reset by the rejected verify — {extended!r}"
        )

    async def _issued_challenge(self, state: str) -> TerminalChallenge:
        email = self.auth_statements.new_user_email()
        requested = await self.auth_statements.request_code_and_capture(email)
        return TerminalChallenge(state=state, email=email, challenge_id=requested.challenge_id, code=requested.code)

    def _watched_keys(self, terminal: TerminalChallenge) -> list[str]:
        return self._keys_that_must_stay_absent(terminal) + [
            POINTER_KEY.format(challenge_type=EMAIL_CODE, uniqueness_key=terminal.email),
            COOLDOWN_KEY.format(challenge_type=EMAIL_CODE, uniqueness_key=terminal.email),
        ]

    @staticmethod
    def _keys_that_must_stay_absent(terminal: TerminalChallenge) -> list[str]:
        return [
            RECORD_KEY.format(challenge_id=terminal.challenge_id),
            VERIFICATION_KEY.format(challenge_id=terminal.challenge_id),
        ]

    async def _assert_record_is_gone(self, terminal: TerminalChallenge) -> None:
        record = RECORD_KEY.format(challenge_id=terminal.challenge_id)
        lifetime = await self._lifetime_of(record)
        assert lifetime == ABSENT_KEY_TTL, (
            f"a challenge {terminal.state} must hold no live record — {record} still lives {lifetime}s"
        )

    @staticmethod
    def _wrong_code(code: str) -> str:
        return ALTERNATE_WRONG_CODE if code == WRONG_CODE else WRONG_CODE

    @staticmethod
    async def _lifetime_of(key: str) -> int:
        redis = Redis(**redis_settings())
        try:
            return int(await redis.ttl(key))
        finally:
            await redis.aclose()

    @staticmethod
    async def _drop_keys(*keys: str) -> None:
        redis = Redis(**redis_settings())
        try:
            await redis.delete(*keys)
        finally:
            await redis.aclose()
