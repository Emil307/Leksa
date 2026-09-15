from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from clients.application.dto.profile.profile_dto import UserRecord
from clients.application.dto.profile.raw_profile_response import RawProfileResponse
from clients.application.profile_client import BEARER_SCHEME, ProfileClient

from statements.access_token import (
    AUDIENCE_CLAIM,
    EXPIRY_CLAIM,
    ID_CLAIM,
    SESSION_CLAIM,
    SUBJECT_CLAIM,
    access_token_claims,
    forge_token,
)
from statements.auth_database import AuthDatabase
from statements.test_data import TestData
from statements.user_records import user_record
from statements.wire_contract import (
    ACCESS_TOKEN_LIFETIME,
    SESSION_LIFETIME,
    assert_unified_authorization_refusal,
)

ACCOUNT_FIELD_NAMES = frozenset({"id", "name", "surname", "email", "isSuperuser"})

REQUIRED_CLAIMS = [SUBJECT_CLAIM, SESSION_CLAIM, ID_CLAIM, EXPIRY_CLAIM, AUDIENCE_CLAIM]

NON_UUID_IDENTIFIERS = [
    (SUBJECT_CLAIM, "not-a-uuid"),
    (SUBJECT_CLAIM, 42),
    (SESSION_CLAIM, "not-a-uuid"),
    (SESSION_CLAIM, ["8f14e45f-ceea-467a-9b8a-3f5b0f6e1d21"]),
    (ID_CLAIM, "not-a-uuid"),
    (ID_CLAIM, None),
]

NON_INTEGER_EXPIRIES = ["1790000000", 1790000000.5, True, None]

NON_STRING_AUDIENCES = [42, ["uwords-api"], None, {"aud": "uwords-api"}]

WRONG_AUDIENCES = ["UWORDS-API", "Uwords-Api", "uwords-api ", "uwords-app"]


@dataclass(frozen=True)
class LiveSession:
    user_id: str
    session_id: str


class JwtClaimsStatements:
    def __init__(self, profile_client: ProfileClient, auth_database: AuthDatabase):
        self.profile_client = profile_client
        self.auth_database = auth_database

    async def sign_in_user(self) -> LiveSession:
        record = self._minimal_account()
        await self.auth_database.store_user(record)

        opened_at = datetime.now(UTC)
        session_id = await self.auth_database.open_session(
            user_id=record.id,
            opened_at=opened_at,
            expires_at=opened_at + SESSION_LIFETIME,
        )
        return LiveSession(user_id=record.id, session_id=session_id)

    async def request_profile_without_claim(self, session: LiveSession, claim: str) -> RawProfileResponse:
        claims = self._valid_claims(session)
        del claims[claim]
        return await self._request_profile_with_claims(claims)

    async def request_profile_with_claim_value(
        self, session: LiveSession, claim: str, value: Any
    ) -> RawProfileResponse:
        claims = self._valid_claims(session)
        claims[claim] = value
        return await self._request_profile_with_claims(claims)

    async def request_profile_with_expiry(self, session: LiveSession, value: Any) -> RawProfileResponse:
        return await self.request_profile_with_claim_value(session, EXPIRY_CLAIM, value)

    async def request_profile_with_audience(self, session: LiveSession, value: Any) -> RawProfileResponse:
        return await self.request_profile_with_claim_value(session, AUDIENCE_CLAIM, value)

    def assert_matches_unified_authorization_refusal(self, outcome: RawProfileResponse) -> None:
        assert_unified_authorization_refusal(outcome.http_status, outcome.body)

    def assert_no_value_was_silently_coerced(self, outcome: RawProfileResponse) -> None:
        assert isinstance(outcome.body, dict), f"the refusal must stay one JSON object, got {outcome.body!r}"
        leaked = ACCOUNT_FIELD_NAMES & frozenset(outcome.body)
        assert not leaked, (
            f"a claim of the wrong type must never be coerced into a verified one; the response leaked {sorted(leaked)}"
        )

    async def _request_profile_with_claims(self, claims: dict[str, Any]) -> RawProfileResponse:
        return await self.profile_client.request_profile(f"{BEARER_SCHEME} {forge_token(claims)}")

    @staticmethod
    def _valid_claims(session: LiveSession) -> dict[str, Any]:
        expires_at = datetime.now(UTC) + ACCESS_TOKEN_LIFETIME
        return access_token_claims(session.user_id, session.session_id, int(expires_at.timestamp()))

    @staticmethod
    def _minimal_account() -> UserRecord:
        return user_record(
            name=TestData.unique_name("claims"),
            email=TestData.unique_email("claims"),
            is_superuser=False,
        )
