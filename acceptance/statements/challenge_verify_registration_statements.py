from dataclasses import dataclass

from clients.application.auth_client import AuthClient
from clients.application.dto.auth.session_dto import SessionDto

from statements.auth_database import AuthDatabase
from statements.auth_statements import (
    AuthStatements,
    assert_exactly_one_session,
    assert_sole_email_account,
    is_canonical_uuid,
)
from statements.outbox_database import OutboxDatabase

EMPTY_NAME = ""
NO_USER = 0
PROMISED_TABLES = ["auth.t_auth", "auth.t_sessions"]


@dataclass(frozen=True)
class UnknownEmailWithCode:
    requested_email: str
    normalized_email: str
    challenge_id: str
    code: str


class ChallengeVerifyRegistrationStatements:
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

    async def given_a_code_requested_for_an_email_no_user_owns(self) -> UnknownEmailWithCode:
        normalized = self.auth_statements.new_user_email()
        requested = f" {normalized.upper()} "

        owners = await self.auth_database.count_users_with_email(normalized)
        assert owners == NO_USER, f"{normalized} must belong to no user before the scenario, found {owners}"

        code_request = await self.auth_statements.request_code_and_capture(requested, queued_for=normalized)

        return UnknownEmailWithCode(
            requested_email=requested,
            normalized_email=normalized,
            challenge_id=code_request.challenge_id,
            code=code_request.code,
        )

    async def verify_code(self, unknown: UnknownEmailWithCode) -> SessionDto:
        session = await self.auth_client.verify_challenge(unknown.challenge_id, unknown.code)
        self.auth_statements.assert_verify_accepted(session)
        return session

    async def assert_exactly_one_user_with_an_empty_name(
        self, session: SessionDto, unknown: UnknownEmailWithCode
    ) -> None:
        users = await self.auth_database.users_with_email(unknown.normalized_email)
        assert users == [(session.user_id, EMPTY_NAME)], (
            f"{unknown.normalized_email} must own exactly one user "
            f"{[(session.user_id, EMPTY_NAME)]!r} with an empty name, found {users!r}"
        )

    async def assert_exactly_one_email_account_for_the_normalized_address(
        self, session: SessionDto, unknown: UnknownEmailWithCode
    ) -> None:
        accounts = await self.auth_database.provider_accounts_of_user(session.user_id)
        assert_sole_email_account(
            accounts, unknown.normalized_email, f"the user registered from {unknown.requested_email!r}"
        )

    async def assert_exactly_one_session_carrying_the_answered_identifier(self, session: SessionDto) -> None:
        assert is_canonical_uuid(session.session_id), (
            f"the issued session must carry a canonical UUID id, got {session.session_id!r}"
        )
        sessions = await self.auth_database.session_ids_of_user(session.user_id)
        assert_exactly_one_session(sessions, session.session_id, "registering the user")

    async def assert_no_profile_and_no_onboarding_row_appears(self, session: SessionDto) -> None:
        holders = await self.auth_database.tables_holding_rows_of_user(session.user_id)
        assert holders == PROMISED_TABLES, (
            f"registration must write the new user into exactly {PROMISED_TABLES!r} — no profile row, "
            f"no onboarding row, nothing else — found {holders!r}"
        )
