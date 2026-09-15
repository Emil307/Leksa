import asyncio
from dataclasses import dataclass

from clients.application.auth_client import AuthClient
from clients.application.dto.auth.session_dto import SessionDto

from statements.auth_database import AuthDatabase
from statements.auth_statements import HTTP_OK, AuthStatements, assert_sole_email_account, is_canonical_uuid
from statements.outbox_database import OutboxDatabase

HTTP_CONFLICT = 409
COOLDOWN_POLL_SECONDS = 1.0
COOLDOWN_POLL_ATTEMPTS = 120


@dataclass(frozen=True)
class Login:
    email: str
    session: SessionDto


class SecondLoginStatements:
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

    async def given_a_user_who_already_logged_in_with_a_code(self) -> Login:
        email = self.auth_statements.new_user_email()
        session = await self._log_in(email)
        assert is_canonical_uuid(session.session_id), (
            f"the first login of {email} must carry a canonical UUID session id, got {session.session_id!r}"
        )
        assert session.refresh_token, f"the first login of {email} must carry a refresh token"
        return Login(email=email, session=session)

    async def log_in_again(self, first: Login) -> SessionDto:
        return await self._log_in(first.email)

    async def assert_the_email_account_is_still_the_only_one(self, first: Login, second: SessionDto) -> None:
        assert second.user_id == first.session.user_id, (
            f"the second login of {first.email} must answer with the same user "
            f"{first.session.user_id!r}, got {second.user_id!r}"
        )
        accounts = await self.auth_database.provider_accounts_of_user(second.user_id)
        assert_sole_email_account(accounts, first.email, f"the user who logged in twice from {first.email!r}")

    def assert_a_second_session_with_another_identifier_and_another_refresh_token(
        self, first: Login, second: SessionDto
    ) -> None:
        assert is_canonical_uuid(second.session_id), (
            f"the second login must carry a canonical UUID session id, got {second.session_id!r}"
        )
        assert second.session_id != first.session.session_id, (
            f"the second login must open a session other than {first.session.session_id!r}, "
            f"got {second.session_id!r} again"
        )
        assert second.refresh_token, "the second login must carry a refresh token"
        assert second.refresh_token != first.session.refresh_token, (
            "the second login must carry a refresh token other than the one the first session holds, "
            "the same token came back"
        )

    async def assert_the_first_session_is_still_stored_beside_the_second(
        self, first: Login, second: SessionDto
    ) -> None:
        expected = [first.session.session_id, second.session_id]
        stored = await self.auth_database.session_ids_of_user(second.user_id)
        assert stored == expected, (
            f"logging in twice from {first.email} must leave exactly {expected!r} in storage — "
            f"the first session kept beside the second — found {stored!r}"
        )

    async def _log_in(self, email: str) -> SessionDto:
        challenge_id = await self._request_a_code_once_the_cooldown_frees(email)
        code = await self.outbox_database.queued_code_for(email)
        assert code is not None, f"a login code must be queued for {email}, the outbox stayed empty"
        session = await self.auth_client.verify_challenge(challenge_id, code)
        self.auth_statements.assert_verify_accepted(session)
        return session

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
            f"{COOLDOWN_POLL_ATTEMPTS * COOLDOWN_POLL_SECONDS} seconds — a second login never became possible"
        )
