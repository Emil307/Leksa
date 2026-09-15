import asyncio
import unicodedata
from dataclasses import dataclass

from clients.application.auth_client import AuthClient
from clients.application.dto.auth.session_dto import SessionDto

from statements.auth_database import AuthDatabase
from statements.auth_statements import HTTP_OK, AuthStatements, assert_sole_email_account
from statements.challenge_start_cooldown_statements import ChallengeStartCooldownStatements, CooldownDenial
from statements.challenge_verify_stored_spelling_statements import mixed_case
from statements.outbox_database import OutboxDatabase
from statements.second_login_statements import COOLDOWN_POLL_ATTEMPTS, COOLDOWN_POLL_SECONDS, HTTP_CONFLICT
from statements.test_data import TestData

ACCENTED_PREFIX = "josé"
TURKISH_PREFIX = "ivan"


@dataclass(frozen=True)
class SpellingPair:
    canonical: str
    first: str
    second: str


class EmailSpellingIdentityStatements:
    def __init__(
        self,
        auth_client: AuthClient,
        auth_statements: AuthStatements,
        auth_database: AuthDatabase,
        outbox_database: OutboxDatabase,
        cooldown_statements: ChallengeStartCooldownStatements,
    ):
        self.auth_client = auth_client
        self.auth_statements = auth_statements
        self.auth_database = auth_database
        self.outbox_database = outbox_database
        self.cooldown_statements = cooldown_statements

    async def given_code_requested_in_another_case(self):
        canonical = self.auth_statements.new_user_email()
        return await self._given_code_requested(SpellingPair(canonical, mixed_case(canonical), canonical))

    async def given_code_requested_in_decomposed_form(self):
        canonical = TestData.unique_email(ACCENTED_PREFIX)
        decomposed = unicodedata.normalize("NFD", canonical)
        assert decomposed != canonical, (
            f"the decomposed spelling of {canonical!r} must differ from its composed form, both read {decomposed!r}"
        )
        return await self._given_code_requested(SpellingPair(canonical, decomposed, canonical))

    async def given_code_requested_with_a_capital_dotted_i(self):
        canonical = TestData.unique_email(TURKISH_PREFIX)
        assert "i" in canonical, f"the address must carry a dotted i to exercise the Turkish casing, got {canonical!r}"
        return await self._given_code_requested(SpellingPair(canonical, canonical.upper(), canonical))

    async def request_code_in_the_other_spelling(self, pair: SpellingPair) -> CooldownDenial:
        return await self.cooldown_statements.request_code_again(pair.second)

    def assert_rejected_by_cooldown(self, denial: CooldownDenial) -> None:
        self.cooldown_statements.assert_rejected_by_cooldown(denial)
        self.cooldown_statements.assert_carries_remaining_wait_in_whole_seconds(denial)

    async def log_in_with_the_first_code(self, requested) -> SessionDto:
        session = await self.auth_client.verify_challenge(requested.challenge_id, requested.code)
        self.auth_statements.assert_verify_accepted(session)
        return session

    async def assert_exactly_one_user_owns_the_address(self, session: SessionDto, pair: SpellingPair) -> None:
        owners = await self.auth_database.user_ids_with_email_ignoring_case_and_spaces(pair.canonical)
        assert owners == [session.user_id], (
            f"{pair.canonical} requested as {pair.first!r} and {pair.second!r} must be owned by exactly "
            f"{[session.user_id]!r} in every spelling, found {owners!r}"
        )
        holders = await self.auth_database.email_identity_user_ids_ignoring_case_and_spaces(pair.canonical)
        assert holders == [session.user_id], (
            f"the email identity of {pair.canonical} must be held by exactly {[session.user_id]!r} "
            f"in every spelling, found {holders!r}"
        )
        accounts = await self.auth_database.provider_accounts_of_user(session.user_id)
        assert_sole_email_account(accounts, pair.canonical, f"the user who logged in from {pair.first!r}")

    async def log_in_again_in_the_other_spelling(self, pair: SpellingPair) -> SessionDto:
        challenge_id = await self._request_a_code_once_the_cooldown_frees(pair.second)
        code = await self.outbox_database.queued_code_for(pair.canonical)
        assert code is not None, f"a login code must be queued for {pair.canonical}, the outbox stayed empty"
        session = await self.auth_client.verify_challenge(challenge_id, code)
        self.auth_statements.assert_verify_accepted(session)
        return session

    def assert_the_same_user_came_back(self, first: SessionDto, second: SessionDto, pair: SpellingPair) -> None:
        assert second.user_id == first.user_id, (
            f"logging in as {pair.second!r} must answer with the same user as {pair.first!r} — "
            f"{first.user_id!r} — got {second.user_id!r}"
        )
        assert second.session_id != first.session_id, (
            f"the repeat login must open a session other than {first.session_id!r}, got it again"
        )

    async def _given_code_requested(self, pair: SpellingPair):
        await self._assert_the_address_is_owned_by_nobody(pair.canonical)
        requested = await self.auth_statements.request_code_and_capture(pair.first, queued_for=pair.canonical)
        assert requested.code.isdigit(), (
            f"the login code queued for {pair.canonical} must be numeric, the outbox held {requested.code!r}"
        )
        return pair, requested

    async def _assert_the_address_is_owned_by_nobody(self, canonical: str) -> None:
        owners = await self.auth_database.user_ids_with_email_ignoring_case_and_spaces(canonical)
        assert owners == [], (
            f"{canonical} must be owned by no user in any spelling before the scenario, found {owners!r}"
        )

    async def _request_a_code_once_the_cooldown_frees(self, email: str) -> str:
        for _ in range(COOLDOWN_POLL_ATTEMPTS):
            challenge = await self.auth_statements.request_code(email)
            if challenge.http_status == HTTP_OK:
                return challenge.challenge_id
            assert challenge.http_status == HTTP_CONFLICT, (
                f"a code request for {email} must be either accepted with {HTTP_OK} or refused on cooldown "
                f"with {HTTP_CONFLICT}, got {challenge.http_status}"
            )
            await asyncio.sleep(COOLDOWN_POLL_SECONDS)
        raise AssertionError(
            f"the resend cooldown for {email} stayed armed for "
            f"{COOLDOWN_POLL_ATTEMPTS * COOLDOWN_POLL_SECONDS} seconds — a repeat login never became possible"
        )
