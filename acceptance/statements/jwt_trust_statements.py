import hashlib
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from clients.application.dto.profile.profile_dto import UserRecord
from clients.application.dto.profile.raw_profile_response import RawProfileResponse
from clients.application.profile_client import BEARER_SCHEME, ProfileClient

from statements.access_token import (
    access_token_claims,
    api_secret,
    forge_token,
    mint_access_token,
    token_resigned_with,
    token_with_tampered_signature,
    unsigned_token,
)
from statements.auth_database import AuthDatabase
from statements.profile_statements import (
    STORED_BIRTHDAY,
    STORED_CREATED_AT,
    STORED_GENDER,
    STORED_UPDATED_AT,
)
from statements.test_data import TestData
from statements.user_records import user_record
from statements.wire_contract import (
    ACCESS_TOKEN_LIFETIME,
    HTTP_OK,
    SESSION_LIFETIME,
    assert_unified_authorization_refusal,
)

FOREIGN_SECRET = "foreign-secret-that-the-server-never-trusts"
OTHER_ALGORITHM_HEADER = {"alg": "HS512", "typ": "JWT"}
NO_ALGORITHM_HEADER = {"alg": "none", "typ": "JWT"}

STORED_PHONE = "+79995550102"


@dataclass(frozen=True)
class TrustedUser:
    record: UserRecord
    session_id: str
    access_token: str


class JwtTrustStatements:
    def __init__(self, profile_client: ProfileClient, auth_database: AuthDatabase):
        self.profile_client = profile_client
        self.auth_database = auth_database

    async def sign_in_user_with_live_session(self) -> TrustedUser:
        record = self._account()
        await self.auth_database.store_user(record)

        now = datetime.now(UTC)
        session_id = await self.auth_database.open_session(
            user_id=record.id,
            opened_at=now,
            expires_at=now + SESSION_LIFETIME,
        )
        token = mint_access_token(
            user_id=record.id,
            session_id=session_id,
            expires_at=now + ACCESS_TOKEN_LIFETIME,
        )
        return TrustedUser(record=record, session_id=session_id, access_token=token)

    @staticmethod
    def token_with_tampered_signature(user: TrustedUser) -> str:
        return token_with_tampered_signature(user.access_token)

    def token_signed_with_a_foreign_secret(self, user: TrustedUser) -> str:
        return token_resigned_with(user.access_token, FOREIGN_SECRET)

    def token_signed_with_another_algorithm(self, user: TrustedUser) -> str:
        return forge_token(self._claims(user), OTHER_ALGORITHM_HEADER, api_secret(), hashlib.sha512)

    def token_without_a_signing_algorithm(self, user: TrustedUser) -> str:
        return unsigned_token(self._claims(user), NO_ALGORITHM_HEADER)

    async def request_profile_with(self, token: str) -> RawProfileResponse:
        return await self.profile_client.request_profile(f"{BEARER_SCHEME} {token}")

    def assert_profile_returned(self, response: RawProfileResponse, user: TrustedUser) -> None:
        assert response.http_status == HTTP_OK, (
            f"a token signed HS256 with the server secret must answer {HTTP_OK}, got {response.http_status}"
        )
        assert isinstance(response.body, dict) and response.body.get("id") == user.record.id, (
            f"the profile must belong to the token subject {user.record.id}, got {response.body}"
        )

    def assert_matches_unified_authorization_refusal(self, response: RawProfileResponse) -> None:
        assert_unified_authorization_refusal(response.http_status, response.body)

    @staticmethod
    def _claims(user: TrustedUser) -> dict[str, Any]:
        expires_at = datetime.now(UTC) + ACCESS_TOKEN_LIFETIME
        return access_token_claims(user.record.id, user.session_id, int(expires_at.timestamp()))

    @staticmethod
    def _account() -> UserRecord:
        return user_record(
            name=TestData.unique_name("name"),
            surname=TestData.unique_name("surname"),
            email=TestData.unique_email("jwt-trust"),
            is_superuser=False,
            created_at=STORED_CREATED_AT,
            updated_at=STORED_UPDATED_AT,
            avatar_id=str(uuid.uuid4()),
            birthday=STORED_BIRTHDAY,
            gender=STORED_GENDER,
            city=TestData.unique_name("city"),
            phone=STORED_PHONE,
        )
