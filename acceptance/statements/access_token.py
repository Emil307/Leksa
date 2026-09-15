import base64
import hashlib
import hmac
import json
import os
import uuid
from datetime import UTC, datetime
from typing import Any

API_AUDIENCE = "uwords-api"
JWT_SECRET_VARIABLE = "JWT_SECRET"

SUBJECT_CLAIM = "sub"
SESSION_CLAIM = "sid"
ID_CLAIM = "jti"
EXPIRY_CLAIM = "exp"
AUDIENCE_CLAIM = "aud"

ROTATED_TOKEN = "the rotated access token"

HS256_HEADER = {"alg": "HS256", "typ": "JWT"}
SEGMENT_SEPARATOR = b"."
BASE64_PADDING = b"="

TAMPERED_SIGNATURE_CHARACTER = "A"
TAMPERED_SIGNATURE_ALTERNATIVE = "B"


def required_value(variable: str) -> str:
    raw = os.environ.get(variable)
    assert raw, f"{variable} must be exported by infrastructure/.env — the test reads it, it never hardcodes it"
    return raw


def api_secret() -> str:
    return required_value(JWT_SECRET_VARIABLE)


def encode_segment(content: dict[str, Any]) -> bytes:
    raw = json.dumps(content, separators=(",", ":"), sort_keys=True).encode("utf-8")
    return base64.urlsafe_b64encode(raw).rstrip(BASE64_PADDING)


def signing_input_of(header: dict[str, Any], claims: dict[str, Any]) -> bytes:
    return encode_segment(header) + SEGMENT_SEPARATOR + encode_segment(claims)


def signature_of(signing_input: bytes, secret: str, digest: Any = hashlib.sha256) -> bytes:
    signed = hmac.new(secret.encode("utf-8"), signing_input, digest).digest()
    return base64.urlsafe_b64encode(signed).rstrip(BASE64_PADDING)


def forge_token(
    claims: dict[str, Any],
    header: dict[str, Any] | None = None,
    secret: str | None = None,
    digest: Any = hashlib.sha256,
) -> str:
    signing_input = signing_input_of(header or HS256_HEADER, claims)
    signature = signature_of(signing_input, secret if secret is not None else api_secret(), digest)
    return (signing_input + SEGMENT_SEPARATOR + signature).decode("ascii")


def unsigned_token(claims: dict[str, Any], header: dict[str, Any]) -> str:
    return (signing_input_of(header, claims) + SEGMENT_SEPARATOR).decode("ascii")


def token_resigned_with(token: str, secret: str, digest: Any = hashlib.sha256) -> str:
    signing_input = token.rpartition(".")[0].encode("ascii")
    signature = signature_of(signing_input, secret, digest)
    return (signing_input + SEGMENT_SEPARATOR + signature).decode("ascii")


def segment_of(token: str, index: int) -> dict[str, Any]:
    segment = token.split(".")[index]
    return json.loads(base64.urlsafe_b64decode(segment + "=" * (-len(segment) % 4)))


def header_of(token: str) -> dict[str, Any]:
    return segment_of(token, 0)


def claims_of(token: str) -> dict[str, Any]:
    return segment_of(token, 1)


def token_with_tampered_signature(token: str) -> str:
    signing_input, _, signature = token.rpartition(".")
    flipped = (
        TAMPERED_SIGNATURE_ALTERNATIVE if signature[0] == TAMPERED_SIGNATURE_CHARACTER else TAMPERED_SIGNATURE_CHARACTER
    )
    return f"{signing_input}.{flipped}{signature[1:]}"


def access_token_claims(user_id: str, session_id: str, expires_at: Any) -> dict[str, Any]:
    return {
        SUBJECT_CLAIM: user_id,
        SESSION_CLAIM: session_id,
        ID_CLAIM: str(uuid.uuid4()),
        EXPIRY_CLAIM: expires_at,
        AUDIENCE_CLAIM: API_AUDIENCE,
    }


def mint_access_token(user_id: str, session_id: str, expires_at: datetime) -> str:
    return forge_token(access_token_claims(user_id, session_id, int(expires_at.timestamp())))


def assert_signed_under_api_secret(token: str, subject: str) -> None:
    assert token_resigned_with(token, api_secret()) == token, (
        f"{subject} must be signed under the API secret, its signature does not verify"
    )


def assert_claims_name_user_session_and_audience(
    claims: dict[str, Any], user_id: str | None, session_id: str | None, subject: str
) -> None:
    expected = {SUBJECT_CLAIM: user_id, SESSION_CLAIM: session_id, AUDIENCE_CLAIM: API_AUDIENCE}
    actual = {name: claims.get(name) for name in expected}
    assert actual == expected, f"{subject} must name {expected!r}, got {actual!r}"


def expiry_of(claims: dict[str, Any], subject: str) -> datetime:
    raw = claims.get(EXPIRY_CLAIM)
    assert isinstance(raw, int), f"{subject} must carry a numeric {EXPIRY_CLAIM}, got {raw!r}"
    return datetime.fromtimestamp(raw, UTC)


def expiry_of_token(token: str | None, subject: str) -> datetime:
    assert token, f"{subject} must be present, the response carried none"
    return expiry_of(claims_of(token), subject)
