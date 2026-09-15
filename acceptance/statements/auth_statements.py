import os
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

from clients.application.auth_client import AuthClient
from clients.application.dto.auth.challenge_dto import ChallengeStartDto
from clients.application.dto.auth.session_dto import SessionDto

from statements.access_token import (
    EXPIRY_CLAIM,
    ID_CLAIM,
    assert_claims_name_user_session_and_audience,
    assert_signed_under_api_secret,
    claims_of,
    expiry_of,
)
from statements.outbox_database import OutboxDatabase
from statements.test_data import TestData
from statements.wire_contract import ACCESS_TOKEN_LIFETIME_VARIABLE, HTTP_OK

EMAIL_CODE = "EMAIL_CODE"
EMAIL_PROVIDER = "email"
CODE_LIFETIME_VARIABLE = "AUTH_CHALLENGE_TTL_SECONDS"
ISSUED_TOKEN = "the issued access token"

CHALLENGE_START_RESPONSE_FIELDS = frozenset({"challengeId", "challengeType", "expiresAt"})


def required_seconds(variable: str) -> int:
    raw = os.environ.get(variable)
    assert raw, f"{variable} must be exported by infrastructure/.env — the test reads it, it never hardcodes it"
    return int(raw)


def assert_instant_is_the_moment_plus_lifetime(
    instant: datetime, requested_at: datetime, responded_at: datetime, lifetime_variable: str, subject: str
) -> None:
    lifetime = timedelta(seconds=required_seconds(lifetime_variable))
    earliest = (requested_at + lifetime).replace(microsecond=0)
    latest = responded_at + lifetime
    assert earliest <= instant <= latest, (
        f"{subject} must fall inside [{earliest.isoformat()}, {latest.isoformat()}] — "
        f"the request moment plus {lifetime_variable} — got {instant.isoformat()}"
    )


def assert_exactly_one_session(session_ids: list[str], session_id: str | None, subject: str) -> None:
    expected = [session_id]
    assert session_ids == expected, (
        f"{subject} must leave exactly {expected!r} in storage — one session, the same row — found {session_ids!r}"
    )


def assert_access_token_issued_for(
    token: str | None,
    user_id: str | None,
    session_id: str | None,
    requested_at: datetime,
    responded_at: datetime,
    subject: str,
) -> None:
    assert token, f"{subject} must be present, the response carried none"
    assert_signed_under_api_secret(token, subject)
    claims = claims_of(token)
    assert_claims_name_user_session_and_audience(claims, user_id, session_id, subject)
    assert_instant_is_the_moment_plus_lifetime(
        expiry_of(claims, subject), requested_at, responded_at, ACCESS_TOKEN_LIFETIME_VARIABLE, f"{subject} expiry"
    )


def assert_access_token_claims_are_well_formed(session: SessionDto) -> None:
    claims = claims_of(session.access_token)
    assert_claims_name_user_session_and_audience(claims, session.user_id, session.session_id, ISSUED_TOKEN)
    assert isinstance(claims.get(EXPIRY_CLAIM), int), (
        f"{ISSUED_TOKEN} must carry a numeric {EXPIRY_CLAIM}, got {claims.get(EXPIRY_CLAIM)!r}"
    )
    assert_id_claim_is_uuid(claims, ISSUED_TOKEN)


def assert_id_claim_is_uuid(claims: dict[str, Any], subject: str) -> None:
    assert is_canonical_uuid(str(claims.get(ID_CLAIM))), (
        f"{subject} must carry a UUID {ID_CLAIM}, got {claims.get(ID_CLAIM)!r}"
    )


@dataclass(frozen=True)
class RequestedCode:
    challenge_id: str
    code: str


def assert_sole_email_account(accounts: list[tuple[str, str]], email: str, subject: str) -> None:
    expected = [(EMAIL_PROVIDER, email)]
    assert accounts == expected, (
        f"{subject} must own exactly {expected!r} — the {EMAIL_PROVIDER} provider account "
        f"for the normalized address — found {accounts!r}"
    )


def is_canonical_uuid(value: str) -> bool:
    try:
        return str(uuid.UUID(value)) == value
    except (ValueError, AttributeError, TypeError):
        return False


class AuthStatements:
    def __init__(self, auth_client: AuthClient, outbox_database: OutboxDatabase):
        self.auth_client = auth_client
        self.outbox_database = outbox_database

    def new_user_email(self) -> str:
        return TestData.unique_email()

    async def request_code(self, email: str) -> ChallengeStartDto:
        return await self.auth_client.start_challenge(email, EMAIL_CODE)

    def assert_challenge_accepted(self, challenge: ChallengeStartDto) -> None:
        assert challenge.http_status == HTTP_OK, (
            f"the code request must be accepted with {HTTP_OK}, got {challenge.http_status}"
        )

    def assert_verify_accepted(self, session: SessionDto) -> None:
        assert session.http_status == HTTP_OK, (
            f"a valid code must be accepted with {HTTP_OK}, got {session.http_status}"
        )

    async def request_code_and_capture(self, requested_email: str, queued_for: str | None = None) -> RequestedCode:
        delivered_to = requested_email if queued_for is None else queued_for

        challenge = await self.request_code(requested_email)
        self.assert_challenge_accepted(challenge)

        code = await self.outbox_database.queued_code_for(delivered_to)
        assert code is not None, f"a login code must be queued for {delivered_to}, the outbox stayed empty"

        return RequestedCode(challenge_id=challenge.challenge_id, code=code)

    async def given_live_session(self) -> SessionDto:
        return await self.given_live_session_of(self.new_user_email())

    async def given_live_session_of(self, email: str) -> SessionDto:
        requested = await self.request_code_and_capture(email)

        session = await self.auth_client.verify_challenge(requested.challenge_id, requested.code)
        self.assert_verify_accepted(session)
        self.assert_session_carries_identifier_and_both_tokens(session)
        return session

    def assert_session_carries_identifier_and_both_tokens(self, session: SessionDto) -> None:
        assert is_canonical_uuid(session.session_id), (
            f"the issued session must carry a canonical UUID id, got {session.session_id!r}"
        )
        assert is_canonical_uuid(session.user_id), (
            f"the issued session must name a canonical UUID user, got {session.user_id!r}"
        )
        assert session.refresh_token, "the issued session must carry a refresh token"
        assert session.access_token, "the issued session must carry an access token"
        assert_access_token_claims_are_well_formed(session)

    def assert_challenge_carries_identifier_and_type(self, challenge: ChallengeStartDto) -> None:
        assert challenge.http_status == HTTP_OK, f"challenge start must answer {HTTP_OK}, got {challenge.http_status}"
        assert is_canonical_uuid(challenge.challenge_id), (
            f"challengeId must be a canonical UUID, got {challenge.challenge_id!r}"
        )
        assert challenge.challenge_type == EMAIL_CODE, (
            f"challengeType must be {EMAIL_CODE}, got {challenge.challenge_type!r}"
        )

    def assert_expiry_is_creation_plus_configured_code_lifetime(self, challenge: ChallengeStartDto) -> None:
        lifetime = timedelta(seconds=required_seconds(CODE_LIFETIME_VARIABLE))
        assert challenge.expires_at is not None, "expiresAt must be an ISO-8601 instant"

        earliest = challenge.requested_at + lifetime
        latest = challenge.responded_at + lifetime
        assert earliest <= challenge.expires_at <= latest, (
            f"expiresAt {challenge.expires_at.isoformat()} must fall inside "
            f"[{earliest.isoformat()}, {latest.isoformat()}] — creation plus {CODE_LIFETIME_VARIABLE}"
        )

    def assert_response_carries_no_code_no_authorize_url_and_no_status(self, challenge: ChallengeStartDto) -> None:
        assert challenge.field_names == CHALLENGE_START_RESPONSE_FIELDS, (
            f"challenge start must answer exactly {sorted(CHALLENGE_START_RESPONSE_FIELDS)}, "
            f"got {sorted(challenge.field_names)}"
        )
