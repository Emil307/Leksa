from datetime import timedelta
from typing import Any

HTTP_OK = 200
HTTP_BAD_REQUEST = 400
HTTP_UNAUTHORIZED = 401

VALIDATION_FAILED = "VALIDATION_FAILED"
ERROR_ENVELOPE_FIELDS = frozenset({"code", "message", "payload"})
MAX_TOKEN_BYTES = 512
REFRESH_TOKEN_INVALID_MESSAGE = "Refresh token is not valid"

UNIFIED_AUTHORIZATION_REFUSAL: dict[str, Any] = {
    "code": "UNAUTHORIZED",
    "message": "Unauthorized",
    "payload": None,
}
UNAUTHORIZED_FIELD_NAMES = ERROR_ENVELOPE_FIELDS

MAX_AUTHORIZATION_HEADER_OCTETS = 4096

SESSION_LIFETIME = timedelta(hours=1)
ACCESS_TOKEN_LIFETIME = timedelta(minutes=15)

ACCESS_TOKEN_LIFETIME_VARIABLE = "ACCESS_TOKEN_TTL_SECONDS"
REFRESH_TOKEN_LIFETIME_VARIABLE = "REFRESH_TOKEN_TTL_SECONDS"

REQUEST_TIMEOUT_SECONDS = 30.0


def validation_refusal(message: str) -> dict[str, Any]:
    return {"code": VALIDATION_FAILED, "message": message, "payload": {}}


INVALID_REFRESH_TOKEN_REFUSAL = validation_refusal(REFRESH_TOKEN_INVALID_MESSAGE)


def assert_error_envelope_shape(body: Any, subject: str) -> None:
    assert isinstance(body, dict), f"{subject} must answer a JSON object, got {body!r}"
    assert frozenset(body) == ERROR_ENVELOPE_FIELDS, (
        f"{subject} must answer exactly {sorted(ERROR_ENVELOPE_FIELDS)}, got {sorted(body)}"
    )


def assert_validation_refusal(http_status: int, body: Any, subject: str) -> None:
    assert http_status == HTTP_BAD_REQUEST, (
        f"{subject} must be refused as invalid input with {HTTP_BAD_REQUEST}, got {http_status} with body {body!r}"
    )
    assert_error_envelope_shape(body, subject)
    assert body.get("code") == VALIDATION_FAILED, (
        f"{subject} must answer error code {VALIDATION_FAILED}, got {body.get('code')!r}"
    )


def assert_unified_authorization_refusal(http_status: int, body: Any) -> None:
    assert http_status == HTTP_UNAUTHORIZED, (
        f"a refused authorization must answer {HTTP_UNAUTHORIZED}, got {http_status} with body {body!r}"
    )
    assert body == UNIFIED_AUTHORIZATION_REFUSAL, (
        f"the refusal must be literally {UNIFIED_AUTHORIZATION_REFUSAL}, got {body!r}"
    )
