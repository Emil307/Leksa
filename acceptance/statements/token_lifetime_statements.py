from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from clients.application.auth_client import AuthClient
from clients.application.dto.auth.challenge_dto import ChallengeStartDto
from clients.application.dto.auth.session_dto import SessionDto

from statements.access_token import claims_of, expiry_of
from statements.auth_database import AuthDatabase
from statements.auth_statements import (
    ISSUED_TOKEN,
    AuthStatements,
    assert_instant_is_the_moment_plus_lifetime,
    required_seconds,
)
from statements.outbox_database import OutboxDatabase
from statements.wire_contract import ACCESS_TOKEN_LIFETIME_VARIABLE, REFRESH_TOKEN_LIFETIME_VARIABLE


@dataclass(frozen=True)
class RequestedChallenge:
    email: str
    challenge: ChallengeStartDto
    code: str


@dataclass(frozen=True)
class IssuedSession:
    session: SessionDto
    requested_at: datetime
    responded_at: datetime


def whole_second_floor(moment: datetime) -> datetime:
    return moment.replace(microsecond=0)


class TokenLifetimeStatements:
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

    async def given_requested_code(self) -> RequestedChallenge:
        email = self.auth_statements.new_user_email()
        challenge = await self.auth_statements.request_code(email)
        self.auth_statements.assert_challenge_accepted(challenge)
        code = await self.outbox_database.queued_code_for(email)
        assert code is not None, f"a login code must be queued for {email}, the outbox stayed empty"
        return RequestedChallenge(email=email, challenge=challenge, code=code)

    def assert_code_expiry_is_request_instant_plus_configured_lifetime(self, requested: RequestedChallenge) -> None:
        self.auth_statements.assert_expiry_is_creation_plus_configured_code_lifetime(requested.challenge)

    async def verify_before_expiry(self, requested: RequestedChallenge) -> IssuedSession:
        expires_at = requested.challenge.expires_at
        assert expires_at is not None, "expiresAt must be an ISO-8601 instant"
        requested_at = datetime.now(UTC)
        assert requested_at < expires_at, (
            f"the verification must happen before {expires_at.isoformat()}, it started at {requested_at.isoformat()}"
        )
        session = await self.auth_client.verify_challenge(requested.challenge.challenge_id, requested.code)
        return IssuedSession(session=session, requested_at=requested_at, responded_at=datetime.now(UTC))

    def assert_verification_accepted(self, issued: IssuedSession) -> None:
        self.auth_statements.assert_verify_accepted(issued.session)

    def assert_access_expiry_is_issue_instant_plus_configured_access_lifetime(self, issued: IssuedSession) -> None:
        assert issued.session.access_token, "the issued session must carry an access token"
        assert_instant_is_the_moment_plus_lifetime(
            expiry_of(claims_of(issued.session.access_token), ISSUED_TOKEN),
            issued.requested_at,
            issued.responded_at,
            ACCESS_TOKEN_LIFETIME_VARIABLE,
            f"{ISSUED_TOKEN} expiry",
        )

    async def assert_session_row_expiry_is_issue_instant_plus_configured_refresh_lifetime(
        self, issued: IssuedSession
    ) -> None:
        lifetime = timedelta(seconds=required_seconds(REFRESH_TOKEN_LIFETIME_VARIABLE))
        assert issued.session.session_id, "the issued session must carry an identifier before its row can be read"
        row = await self.auth_database.stored_session_row(issued.session.session_id)
        created_at, expires_at = row.created_at, row.expires_at
        assert expires_at - created_at == lifetime, (
            f"the session row must live exactly {lifetime} — {REFRESH_TOKEN_LIFETIME_VARIABLE} — "
            f"found {expires_at - created_at} between {created_at.isoformat()} and {expires_at.isoformat()}"
        )
        earliest = whole_second_floor(issued.requested_at)
        latest = whole_second_floor(issued.responded_at)
        assert earliest <= created_at <= latest, (
            f"the session row must be created at the issuance instant, inside "
            f"[{earliest.isoformat()}, {latest.isoformat()}], found {created_at.isoformat()}"
        )
