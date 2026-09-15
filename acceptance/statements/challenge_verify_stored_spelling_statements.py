import re
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime

from clients.application.auth_client import AuthClient
from clients.application.dto.auth.session_dto import SessionDto
from clients.application.dto.profile.profile_dto import UserRecord

from statements.auth_database import AuthDatabase
from statements.auth_statements import (
    EMAIL_PROVIDER,
    AuthStatements,
    assert_exactly_one_session,
    assert_sole_email_account,
)
from statements.outbox_database import OutboxDatabase

SEEDED_NAME = "learner"
NO_OWNER: list[str] = []
LOWERCASE_RUN = re.compile(r"[a-z]+")


def mixed_case(email: str) -> str:
    return LOWERCASE_RUN.sub(lambda run: run.group().capitalize(), email)


@dataclass(frozen=True)
class SeededUserWithCode:
    stored_email: str
    requested_email: str
    user_id: str
    challenge_id: str
    code: str


class ChallengeVerifyStoredSpellingStatements:
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

    async def given_user_stored_in_another_case_holding_a_code(self) -> SeededUserWithCode:
        requested = self.auth_statements.new_user_email()
        return await self._given_user_stored_as(mixed_case(requested), requested)

    async def given_user_stored_with_surrounding_spaces_holding_a_code(self) -> SeededUserWithCode:
        requested = self.auth_statements.new_user_email()
        return await self._given_user_stored_as(f" {requested} ", requested)

    async def verify_code(self, seeded: SeededUserWithCode) -> SessionDto:
        session = await self.auth_client.verify_challenge(seeded.challenge_id, seeded.code)
        self.auth_statements.assert_verify_accepted(session)
        return session

    def assert_session_belongs_to_the_stored_user(self, session: SessionDto, seeded: SeededUserWithCode) -> None:
        assert session.user_id == seeded.user_id, (
            f"verify must answer with the user already stored as {seeded.stored_email!r} — "
            f"{seeded.user_id!r} — got {session.user_id!r}"
        )

    async def assert_the_session_is_the_stored_users_only_one(
        self, session: SessionDto, seeded: SeededUserWithCode
    ) -> None:
        sessions = await self.auth_database.session_ids_of_user(seeded.user_id)
        assert_exactly_one_session(
            sessions, session.session_id, f"verifying the user stored as {seeded.stored_email!r}"
        )

    async def assert_no_second_user_owns_the_address_in_any_spelling(self, seeded: SeededUserWithCode) -> None:
        owners = await self.auth_database.user_ids_with_email_ignoring_case_and_spaces(seeded.requested_email)
        assert owners == [seeded.user_id], (
            f"{seeded.requested_email} must be owned by exactly the seeded user {[seeded.user_id]!r} "
            f"in every spelling, found {owners!r}"
        )

    async def assert_email_account_points_at_the_stored_user(self, seeded: SeededUserWithCode) -> None:
        accounts = await self.auth_database.provider_accounts_of_user(seeded.user_id)
        assert_sole_email_account(accounts, seeded.requested_email, f"the user stored as {seeded.stored_email!r}")

    async def assert_no_second_identity_holds_the_address_in_any_spelling(self, seeded: SeededUserWithCode) -> None:
        holders = await self.auth_database.email_identity_user_ids_ignoring_case_and_spaces(seeded.requested_email)
        assert holders == [seeded.user_id], (
            f"the {EMAIL_PROVIDER} identity of {seeded.requested_email} must be held by exactly "
            f"{[seeded.user_id]!r} in every spelling, found {holders!r}"
        )

    async def _given_user_stored_as(self, stored_email: str, requested_email: str) -> SeededUserWithCode:
        await self._assert_the_address_is_owned_by_nobody(requested_email)

        record = self._account_stored_as(stored_email)
        await self.auth_database.store_user(record)
        await self._assert_the_row_kept_the_stored_spelling(record, requested_email)

        requested = await self.auth_statements.request_code_and_capture(requested_email)
        assert requested.code.isdigit(), (
            f"the login code queued for {requested_email} must be numeric, the outbox held {requested.code!r}"
        )

        return SeededUserWithCode(
            stored_email=stored_email,
            requested_email=requested_email,
            user_id=record.id,
            challenge_id=requested.challenge_id,
            code=requested.code,
        )

    async def _assert_the_address_is_owned_by_nobody(self, requested_email: str) -> None:
        owners = await self.auth_database.user_ids_with_email_ignoring_case_and_spaces(requested_email)
        assert owners == NO_OWNER, (
            f"{requested_email} must be owned by no user in any spelling before the scenario, found {owners!r}"
        )

    async def _assert_the_row_kept_the_stored_spelling(self, record: UserRecord, requested_email: str) -> None:
        stored = await self.auth_database.users_with_email(record.email)
        assert stored == [(record.id, SEEDED_NAME)], (
            f"the seeded row must keep the literal spelling {record.email!r} — looking it up verbatim found {stored!r}"
        )
        normalized = await self.auth_database.users_with_email(requested_email)
        assert normalized == [], (
            f"no row may carry the normalized spelling {requested_email!r} before the scenario, found {normalized!r}"
        )

    @staticmethod
    def _account_stored_as(stored_email: str) -> UserRecord:
        now = datetime.now(UTC)
        return UserRecord(
            id=str(uuid.uuid4()),
            name=SEEDED_NAME,
            surname=None,
            email=stored_email,
            is_superuser=False,
            created_at=now,
            updated_at=now,
            avatar_id=None,
            birthday=None,
            gender=None,
            city=None,
            phone=None,
        )
