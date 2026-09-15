from dataclasses import dataclass
from datetime import UTC, datetime

from clients.application.auth_client import AuthClient
from clients.application.dto.auth.session_dto import SessionDto

from statements.auth_database import AuthDatabase
from statements.auth_statements import (
    AuthStatements,
    assert_access_token_issued_for,
    assert_exactly_one_session,
)
from statements.outbox_database import OutboxDatabase

REPLAYED_TOKEN = "the replayed access token"


@dataclass(frozen=True)
class FirstLogin:
    email: str
    challenge_id: str
    code: str
    session: SessionDto


@dataclass(frozen=True)
class Replay:
    session: SessionDto
    requested_at: datetime
    responded_at: datetime


class SameSessionReplayStatements:
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

    async def given_a_user_who_just_logged_in_with_a_code(self) -> FirstLogin:
        email = self.auth_statements.new_user_email()
        requested = await self.auth_statements.request_code_and_capture(email)

        session = await self.auth_client.verify_challenge(requested.challenge_id, requested.code)

        self.auth_statements.assert_verify_accepted(session)
        self.auth_statements.assert_session_carries_identifier_and_both_tokens(session)
        return FirstLogin(
            email=email,
            challenge_id=requested.challenge_id,
            code=requested.code,
            session=session,
        )

    async def repeat_the_same_challenge_and_code(self, first: FirstLogin) -> Replay:
        requested_at = datetime.now(UTC)
        session = await self.auth_client.verify_challenge(first.challenge_id, first.code)
        responded_at = datetime.now(UTC)
        return Replay(session=session, requested_at=requested_at, responded_at=responded_at)

    def assert_the_same_session_identifier_and_refresh_token(self, first: FirstLogin, replay: Replay) -> None:
        self.auth_statements.assert_verify_accepted(replay.session)
        assert replay.session.user_id == first.session.user_id, (
            f"the replay of the challenge of {first.email} must answer with the same user "
            f"{first.session.user_id!r}, got {replay.session.user_id!r}"
        )
        assert replay.session.session_id == first.session.session_id, (
            f"the replay must answer with the session {first.session.session_id!r} the first verification opened, "
            f"got {replay.session.session_id!r}"
        )
        assert replay.session.refresh_token == first.session.refresh_token, (
            "the replay must carry the very refresh token the first verification issued, another token came back"
        )

    def assert_the_access_token_is_signed_anew(self, first: FirstLogin, replay: Replay) -> None:
        assert_access_token_issued_for(
            replay.session.access_token,
            first.session.user_id,
            first.session.session_id,
            replay.requested_at,
            replay.responded_at,
            REPLAYED_TOKEN,
        )

    async def assert_exactly_one_session_of_the_user(self, first: FirstLogin) -> None:
        stored = await self.auth_database.session_ids_of_user(first.session.user_id)
        assert_exactly_one_session(stored, first.session.session_id, f"replaying the challenge of {first.email}")
