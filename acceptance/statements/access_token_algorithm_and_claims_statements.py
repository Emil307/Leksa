import hashlib
from dataclasses import dataclass
from datetime import UTC, datetime

from clients.application.auth_client import AuthClient
from clients.application.dto.auth.session_dto import SessionDto
from clients.application.dto.profile.raw_profile_response import RawProfileResponse
from clients.application.profile_client import BEARER_SCHEME, ProfileClient

from statements.access_token import (
    AUDIENCE_CLAIM,
    EXPIRY_CLAIM,
    HS256_HEADER,
    ID_CLAIM,
    ROTATED_TOKEN,
    SESSION_CLAIM,
    SUBJECT_CLAIM,
    api_secret,
    assert_claims_name_user_session_and_audience,
    assert_signed_under_api_secret,
    claims_of,
    expiry_of_token,
    forge_token,
    header_of,
)
from statements.auth_statements import (
    AuthStatements,
    assert_id_claim_is_uuid,
    assert_instant_is_the_moment_plus_lifetime,
)
from statements.jwt_trust_statements import OTHER_ALGORITHM_HEADER
from statements.session_refresh_statements import SessionRefreshStatements
from statements.wire_contract import ACCESS_TOKEN_LIFETIME_VARIABLE, assert_unified_authorization_refusal

ALLOWED_CLAIM_NAMES = frozenset({SUBJECT_CLAIM, SESSION_CLAIM, ID_CLAIM, EXPIRY_CLAIM, AUDIENCE_CLAIM})


@dataclass(frozen=True)
class RotatedAccessToken:
    previous: SessionDto
    rotated: SessionDto
    requested_at: datetime
    responded_at: datetime


class AccessTokenAlgorithmAndClaimsStatements:
    def __init__(
        self,
        auth_client: AuthClient,
        auth_statements: AuthStatements,
        session_refresh_statements: SessionRefreshStatements,
        profile_client: ProfileClient,
    ):
        self.auth_client = auth_client
        self.auth_statements = auth_statements
        self.session_refresh_statements = session_refresh_statements
        self.profile_client = profile_client

    async def given_live_session(self) -> SessionDto:
        return await self.auth_statements.given_live_session()

    async def rotate_tokens(self, session: SessionDto) -> RotatedAccessToken:
        requested_at = datetime.now(UTC)
        rotated = await self.auth_client.refresh_session(session.refresh_token)
        responded_at = datetime.now(UTC)
        self.session_refresh_statements.assert_rotation_succeeded(rotated)
        return RotatedAccessToken(
            previous=session, rotated=rotated, requested_at=requested_at, responded_at=responded_at
        )

    def assert_new_access_token_is_signed_with_hs256(self, rotation: RotatedAccessToken) -> None:
        header = header_of(rotation.rotated.access_token)
        assert header == HS256_HEADER, f"{ROTATED_TOKEN} must carry the header {HS256_HEADER!r}, got {header!r}"

    def assert_signature_verifies_with_the_configured_secret(self, rotation: RotatedAccessToken) -> None:
        assert_signed_under_api_secret(rotation.rotated.access_token, ROTATED_TOKEN)

    def assert_token_names_the_previous_user_and_session(self, rotation: RotatedAccessToken) -> None:
        assert_claims_name_user_session_and_audience(
            claims_of(rotation.rotated.access_token),
            rotation.previous.user_id,
            rotation.previous.session_id,
            ROTATED_TOKEN,
        )

    def assert_token_carries_exact_expiry(self, rotation: RotatedAccessToken) -> None:
        assert_instant_is_the_moment_plus_lifetime(
            expiry_of_token(rotation.rotated.access_token, ROTATED_TOKEN),
            rotation.requested_at,
            rotation.responded_at,
            ACCESS_TOKEN_LIFETIME_VARIABLE,
            f"{ROTATED_TOKEN} expiry",
        )

    def assert_token_carries_no_extra_claims(self, rotation: RotatedAccessToken) -> None:
        claims = claims_of(rotation.rotated.access_token)
        assert frozenset(claims) == ALLOWED_CLAIM_NAMES, (
            f"{ROTATED_TOKEN} must carry exactly {sorted(ALLOWED_CLAIM_NAMES)}, got {sorted(claims)}"
        )
        assert_id_claim_is_uuid(claims, ROTATED_TOKEN)

    async def request_profile_with_substituted_algorithm(self, rotation: RotatedAccessToken) -> RawProfileResponse:
        substituted = forge_token(
            claims_of(rotation.rotated.access_token), OTHER_ALGORITHM_HEADER, api_secret(), hashlib.sha512
        )
        return await self.profile_client.request_profile(f"{BEARER_SCHEME} {substituted}")

    def assert_matches_unified_authorization_refusal(self, response: RawProfileResponse) -> None:
        assert_unified_authorization_refusal(response.http_status, response.body)
