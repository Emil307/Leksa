import uuid
from dataclasses import dataclass
from datetime import UTC, datetime

from clients.application.auth_client import AuthClient
from clients.application.dto.auth.session_dto import SessionDto
from clients.application.dto.profile.profile_dto import UserRecord

from statements.auth_database import AuthDatabase
from statements.auth_statements import AuthStatements
from statements.outbox_database import OutboxDatabase

REGISTERED_NAME = "learner"
SINGLE_USER = 1


@dataclass(frozen=True)
class RegisteredUserWithCode:
    email: str
    user_id: str
    challenge_id: str
    code: str


class ChallengeVerifyStatements:
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

    async def given_registered_user_holding_a_valid_code(self) -> RegisteredUserWithCode:
        record = self._registered_account()
        await self.auth_database.store_user(record)

        requested = await self.auth_statements.request_code_and_capture(record.email)

        return RegisteredUserWithCode(
            email=record.email,
            user_id=record.id,
            challenge_id=requested.challenge_id,
            code=requested.code,
        )

    async def verify_code(self, registered: RegisteredUserWithCode) -> SessionDto:
        return await self.auth_client.verify_challenge(registered.challenge_id, registered.code)

    def assert_session_belongs_to_the_existing_user(
        self, session: SessionDto, registered: RegisteredUserWithCode
    ) -> None:
        self.auth_statements.assert_verify_accepted(session)
        assert session.user_id == registered.user_id, (
            f"verify must answer with the existing user id {registered.user_id!r}, got {session.user_id!r}"
        )

    def assert_session_carries_identifier_and_both_tokens(self, session: SessionDto) -> None:
        self.auth_statements.assert_session_carries_identifier_and_both_tokens(session)

    async def assert_no_second_user_was_created(self, registered: RegisteredUserWithCode) -> None:
        stored = await self.auth_database.count_users_with_email(registered.email)
        assert stored == SINGLE_USER, f"{registered.email} must keep exactly {SINGLE_USER} account row, found {stored}"
        identities = await self.auth_database.email_identity_user_ids(registered.email)
        assert identities == [registered.user_id], (
            f"{registered.email} must resolve to the single seeded user {registered.user_id!r}, found {identities!r}"
        )

    def _registered_account(self) -> UserRecord:
        now = datetime.now(UTC)
        return UserRecord(
            id=str(uuid.uuid4()),
            name=REGISTERED_NAME,
            surname=None,
            email=self.auth_statements.new_user_email(),
            is_superuser=False,
            created_at=now,
            updated_at=now,
            avatar_id=None,
            birthday=None,
            gender=None,
            city=None,
            phone=None,
        )
