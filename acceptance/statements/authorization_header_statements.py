from dataclasses import dataclass
from datetime import UTC, datetime

from clients.application.dto.profile.raw_profile_response import RawProfileResponse
from clients.application.profile_client import BEARER_SCHEME, ProfileClient

from statements.access_token import mint_access_token
from statements.auth_database import AuthDatabase
from statements.test_data import TestData
from statements.user_records import user_record
from statements.wire_contract import (
    ACCESS_TOKEN_LIFETIME,
    HTTP_OK,
    MAX_AUTHORIZATION_HEADER_OCTETS,
    SESSION_LIFETIME,
    assert_unified_authorization_refusal,
)

MULTIBYTE_PADDING_CHARACTER = "é"
MULTIBYTE_PADDING_LENGTH = 3000


@dataclass(frozen=True)
class SignedInUser:
    user_id: str
    access_token: str


class AuthorizationHeaderStatements:
    def __init__(self, profile_client: ProfileClient, auth_database: AuthDatabase):
        self.profile_client = profile_client
        self.auth_database = auth_database

    async def sign_in_user(self) -> SignedInUser:
        record = user_record(
            name=TestData.unique_name("name"),
            email=TestData.unique_email("header-limit"),
            is_superuser=False,
        )
        await self.auth_database.store_user(record)

        now = datetime.now(UTC)
        session_id = await self.auth_database.open_session(
            user_id=record.id,
            opened_at=now,
            expires_at=now + SESSION_LIFETIME,
        )

        return SignedInUser(
            user_id=record.id,
            access_token=mint_access_token(
                user_id=record.id,
                session_id=session_id,
                expires_at=now + ACCESS_TOKEN_LIFETIME,
            ),
        )

    def credential_at_the_wire_byte_limit(self, user: SignedInUser) -> bytes:
        return self.credential_of_exactly(user, MAX_AUTHORIZATION_HEADER_OCTETS)

    def credential_one_wire_byte_past_the_limit(self, user: SignedInUser) -> bytes:
        return self.credential_of_exactly(user, MAX_AUTHORIZATION_HEADER_OCTETS + 1)

    def credential_of_exactly(self, user: SignedInUser, octets: int) -> bytes:
        separator = octets - len(BEARER_SCHEME) - len(user.access_token)
        assert separator >= 1, (
            f"a credential of {octets} octets cannot hold the scheme and a {len(user.access_token)}-octet token"
        )

        credential = f"{BEARER_SCHEME}{' ' * separator}{user.access_token}".encode("ascii")
        assert len(credential) == octets, f"the credential must be exactly {octets} octets, got {len(credential)}"
        return credential

    def credential_with_more_octets_than_code_points(self) -> bytes:
        value = f"{BEARER_SCHEME} " + MULTIBYTE_PADDING_CHARACTER * MULTIBYTE_PADDING_LENGTH
        credential = value.encode("utf-8")

        assert len(value) <= MAX_AUTHORIZATION_HEADER_OCTETS, (
            f"the credential must stay below the limit in code points, got {len(value)}"
        )
        assert len(credential) > MAX_AUTHORIZATION_HEADER_OCTETS, (
            f"the credential must exceed the limit in wire bytes, got {len(credential)}"
        )
        return credential

    async def request_profile_with(self, credential: bytes) -> RawProfileResponse:
        return await self.profile_client.request_profile(credential)

    def assert_profile_of_owner_returned(self, probe: RawProfileResponse, user: SignedInUser) -> None:
        assert probe.http_status == HTTP_OK, (
            f"a credential of exactly {MAX_AUTHORIZATION_HEADER_OCTETS} wire bytes must answer "
            f"{HTTP_OK}, got {probe.http_status} with body {probe.raw_text!r}"
        )
        assert isinstance(probe.body, dict) and probe.body.get("id") == user.user_id, (
            f"the profile must belong to the token owner {user.user_id}, got body {probe.raw_text!r}"
        )

    def assert_unified_authorization_refusal(self, probe: RawProfileResponse) -> None:
        assert_unified_authorization_refusal(probe.http_status, probe.body)
