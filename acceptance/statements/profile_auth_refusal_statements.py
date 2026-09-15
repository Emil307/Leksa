import uuid
from datetime import UTC, datetime, timedelta

from clients.application.dto.profile.raw_profile_response import RawProfileResponse
from clients.application.profile_client import BEARER_SCHEME, ProfileClient

from statements.access_token import (
    claims_of,
    forge_token,
    mint_access_token,
    token_with_tampered_signature,
)
from statements.auth_database import AuthDatabase
from statements.profile_statements import CLIENT_FIELD_NAMES, ProfileStatements, SignedInUser
from statements.wire_contract import (
    ACCESS_TOKEN_LIFETIME,
    MAX_AUTHORIZATION_HEADER_OCTETS,
    SESSION_LIFETIME,
    assert_unified_authorization_refusal,
)

FOREIGN_SECRET = "a-secret-this-api-never-signed-with"
FOREIGN_AUDIENCE = "uwords-somewhere-else"
FOREIGN_ALGORITHM_HEADER = {"alg": "HS512", "typ": "JWT"}

AUTHORIZATION_VARIANTS = (
    "missing_header",
    "empty_header",
    "other_scheme",
    "bearer_without_token",
    "bearer_with_extra_value",
    "header_over_octet_limit",
    "token_without_jwt_structure",
    "tampered_signature",
    "foreign_secret",
    "foreign_algorithm",
    "missing_required_claim",
    "malformed_claim_type",
    "foreign_audience",
    "expired_token",
    "unknown_session",
    "session_of_another_user",
    "expired_session",
    "absent_account",
)


def _bearer(token: str) -> str:
    return f"{BEARER_SCHEME} {token}"


class ProfileAuthRefusalStatements:
    def __init__(
        self,
        profile_client: ProfileClient,
        profile_statements: ProfileStatements,
        auth_database: AuthDatabase,
    ):
        self.profile_client = profile_client
        self.profile_statements = profile_statements
        self.auth_database = auth_database

    async def sign_in_user(self) -> SignedInUser:
        return await self.profile_statements.sign_in_user_with_every_field_filled()

    async def request_profile_with_variant(self, variant: str, user: SignedInUser) -> RawProfileResponse:
        build_header = getattr(self, f"_header_{variant}")
        return await self.profile_client.request_profile(await build_header(user))

    def assert_refused_with_unified_authorization_refusal(self, refusal: RawProfileResponse) -> None:
        assert_unified_authorization_refusal(refusal.http_status, refusal.body)

    def assert_profile_is_not_returned(self, refusal: RawProfileResponse, user: SignedInUser) -> None:
        leaked_fields = CLIENT_FIELD_NAMES & refusal.field_names
        assert not leaked_fields, f"a refusal must carry no account property, found {sorted(leaked_fields)}"
        for value in (user.record.id, user.record.email, user.record.phone, user.record.name, user.record.city):
            assert value not in refusal.raw_text, "a refusal must not echo any stored account value"

    async def _header_missing_header(self, user: SignedInUser) -> None:
        return None

    async def _header_empty_header(self, user: SignedInUser) -> str:
        return ""

    async def _header_other_scheme(self, user: SignedInUser) -> str:
        return f"Basic {user.access_token}"

    async def _header_bearer_without_token(self, user: SignedInUser) -> str:
        return BEARER_SCHEME

    async def _header_bearer_with_extra_value(self, user: SignedInUser) -> str:
        return f"{_bearer(user.access_token)} {user.access_token}"

    async def _header_header_over_octet_limit(self, user: SignedInUser) -> str:
        padding = "a" * (MAX_AUTHORIZATION_HEADER_OCTETS + 1)
        return _bearer(user.access_token + padding)

    async def _header_token_without_jwt_structure(self, user: SignedInUser) -> str:
        return _bearer("this-value-is-not-a-json-web-token")

    async def _header_tampered_signature(self, user: SignedInUser) -> str:
        return _bearer(token_with_tampered_signature(user.access_token))

    async def _header_foreign_secret(self, user: SignedInUser) -> str:
        return _bearer(forge_token(claims_of(user.access_token), secret=FOREIGN_SECRET))

    async def _header_foreign_algorithm(self, user: SignedInUser) -> str:
        return _bearer(forge_token(claims_of(user.access_token), header=FOREIGN_ALGORITHM_HEADER))

    async def _header_missing_required_claim(self, user: SignedInUser) -> str:
        claims = claims_of(user.access_token)
        claims.pop("jti")
        return _bearer(forge_token(claims))

    async def _header_malformed_claim_type(self, user: SignedInUser) -> str:
        claims = claims_of(user.access_token)
        claims["exp"] = str(claims["exp"])
        return _bearer(forge_token(claims))

    async def _header_foreign_audience(self, user: SignedInUser) -> str:
        claims = claims_of(user.access_token)
        claims["aud"] = FOREIGN_AUDIENCE
        return _bearer(forge_token(claims))

    async def _header_expired_token(self, user: SignedInUser) -> str:
        claims = claims_of(user.access_token)
        claims["exp"] = int(datetime.now(UTC).timestamp()) - 1
        return _bearer(forge_token(claims))

    async def _header_unknown_session(self, user: SignedInUser) -> str:
        return _bearer(self._mint(user.record.id, str(uuid.uuid4())))

    async def _header_session_of_another_user(self, user: SignedInUser) -> str:
        other = await self.profile_statements.sign_in_user_with_every_field_filled()
        return _bearer(self._mint(user.record.id, str(claims_of(other.access_token)["sid"])))

    async def _header_expired_session(self, user: SignedInUser) -> str:
        now = datetime.now(UTC)
        session_id = await self.auth_database.open_session(
            user_id=user.record.id, opened_at=now - SESSION_LIFETIME, expires_at=now - timedelta(seconds=1)
        )
        return _bearer(self._mint(user.record.id, session_id))

    async def _header_absent_account(self, user: SignedInUser) -> str:
        now = datetime.now(UTC)
        orphan_user_id = str(uuid.uuid4())
        session_id = await self.auth_database.open_session(
            user_id=orphan_user_id, opened_at=now, expires_at=now + SESSION_LIFETIME
        )
        return _bearer(self._mint(orphan_user_id, session_id))

    @staticmethod
    def _mint(user_id: str, session_id: str) -> str:
        return mint_access_token(
            user_id=user_id, session_id=session_id, expires_at=datetime.now(UTC) + ACCESS_TOKEN_LIFETIME
        )
