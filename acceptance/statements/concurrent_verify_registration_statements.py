import asyncio
from dataclasses import dataclass

from clients.application.auth_client import AuthClient
from clients.application.dto.auth.session_dto import SessionDto

from statements.auth_database import AuthDatabase
from statements.auth_statements import HTTP_OK, AuthStatements, assert_sole_email_account, is_canonical_uuid
from statements.outbox_database import OutboxDatabase

NO_USER = 0
CONCURRENT_VERIFICATIONS = 2


@dataclass(frozen=True)
class UnclaimedEmailWithCode:
    email: str
    challenge_id: str
    code: str


@dataclass(frozen=True)
class RaceOutcome:
    first: SessionDto
    second: SessionDto

    @property
    def statuses(self) -> list[int]:
        return [self.first.http_status, self.second.http_status]

    @property
    def user_ids(self) -> list[str]:
        return [self.first.user_id, self.second.user_id]


class ConcurrentVerifyRegistrationStatements:
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

    async def given_a_working_code_for_an_email_no_user_owns(self) -> UnclaimedEmailWithCode:
        email = self.auth_statements.new_user_email()

        owners = await self.auth_database.count_users_with_email(email)
        assert owners == NO_USER, f"{email} must belong to no user before the scenario, found {owners}"

        requested = await self.auth_statements.request_code_and_capture(email)

        return UnclaimedEmailWithCode(email=email, challenge_id=requested.challenge_id, code=requested.code)

    async def release_two_verifications_together(self, unclaimed: UnclaimedEmailWithCode) -> RaceOutcome:
        first, second = await asyncio.gather(
            *(
                self.auth_client.verify_challenge(unclaimed.challenge_id, unclaimed.code)
                for _ in range(CONCURRENT_VERIFICATIONS)
            )
        )
        return RaceOutcome(first=first, second=second)

    async def assert_exactly_one_user_owns_the_email(self, unclaimed: UnclaimedEmailWithCode) -> None:
        users = await self.auth_database.user_ids_with_email_ignoring_case_and_spaces(unclaimed.email)
        assert len(users) == 1, (
            f"two concurrent verifications for {unclaimed.email} must leave exactly one user, found {users!r}"
        )

    async def assert_exactly_one_email_account_for_that_user(self, unclaimed: UnclaimedEmailWithCode) -> None:
        owners = await self.auth_database.email_identity_user_ids_ignoring_case_and_spaces(unclaimed.email)
        assert len(owners) == 1, (
            f"two concurrent verifications for {unclaimed.email} must leave exactly one email provider account, "
            f"found accounts of users {owners!r}"
        )
        accounts = await self.auth_database.provider_accounts_of_user(owners[0])
        assert_sole_email_account(accounts, unclaimed.email, f"the user auto-registered from {unclaimed.email}")

    def assert_the_race_loser_got_a_session_not_a_uniqueness_violation(self, outcome: RaceOutcome) -> None:
        expected = [HTTP_OK] * CONCURRENT_VERIFICATIONS
        assert outcome.statuses == expected, (
            f"both concurrent verifications must answer {HTTP_OK} with a session — the race loser must not "
            f"surface a uniqueness violation — got {outcome.statuses!r}"
        )
        for user_id in outcome.user_ids:
            assert is_canonical_uuid(user_id), f"each answered session must carry a canonical user id, got {user_id!r}"

    def assert_both_sessions_belong_to_the_same_user(self, outcome: RaceOutcome) -> None:
        assert outcome.first.user_id == outcome.second.user_id, (
            f"both concurrent verifications must answer for the one created user, "
            f"got {outcome.first.user_id!r} and {outcome.second.user_id!r}"
        )
