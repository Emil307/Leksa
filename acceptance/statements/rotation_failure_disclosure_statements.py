import uuid
from dataclasses import dataclass
from typing import Any

from clients.application.auth_client import AuthClient

from statements.access_token import JWT_SECRET_VARIABLE, required_value
from statements.auth_statements import AuthStatements
from statements.session_row_lock import SessionRowLock
from statements.wire_contract import (
    INVALID_REFRESH_TOKEN_REFUSAL,
    assert_error_envelope_shape,
    assert_unified_authorization_refusal,
    assert_validation_refusal,
)

FORGED_LOG_LINE = "\r\nlevel=INFO forged=true"
OVERLONG_REPEAT = 16
INTERNAL_DETAIL_TRACES = (
    "exception",
    "traceback",
    "stack",
    "com.uwords",
    "org.springframework",
    "hibernate",
    "jdbc",
    "sqlstate",
    "select ",
    "update ",
    "t_sessions",
    "constraint",
    ".java",
    "/backend/",
)


@dataclass(frozen=True)
class SecretSentinel:
    label: str
    marker: str
    presented_token: str


@dataclass(frozen=True)
class RefusedRotation:
    label: str
    http_status: int
    body: Any
    raw_text: str


class RotationFailureDisclosureStatements:
    def __init__(self, auth_client: AuthClient, auth_statements: AuthStatements, session_row_lock: SessionRowLock):
        self.auth_client = auth_client
        self.auth_statements = auth_statements
        self.session_row_lock = session_row_lock

    def sentinel_with_forged_log_line(self) -> SecretSentinel:
        marker = self._marker()
        return SecretSentinel(
            label="токен с поддельной строкой журнала", marker=marker, presented_token=f"{marker}{FORGED_LOG_LINE}"
        )

    def sentinel_longer_than_the_token_limit(self) -> SecretSentinel:
        marker = self._marker()
        return SecretSentinel(label="токен длиннее лимита", marker=marker, presented_token=marker * OVERLONG_REPEAT)

    def sentinel_unknown_to_the_storage(self) -> SecretSentinel:
        marker = self._marker()
        return SecretSentinel(label="неизвестный токен", marker=marker, presented_token=marker)

    async def sentinel_whose_storage_row_is_locked(self) -> SecretSentinel:
        session = await self.auth_statements.given_live_session()
        await self.session_row_lock.hold(session.session_id)
        return SecretSentinel(
            label="отказ хранилища", marker=session.refresh_token, presented_token=session.refresh_token
        )

    async def refresh_with(self, sentinel: SecretSentinel) -> RefusedRotation:
        refusal = await self.auth_client.refresh_session_capturing_refusal(sentinel.presented_token)
        return RefusedRotation(
            label=sentinel.label, http_status=refusal.http_status, body=refusal.body, raw_text=refusal.raw_text
        )

    def assert_refused_as_validation_failure(self, refusal: RefusedRotation) -> None:
        assert_validation_refusal(refusal.http_status, refusal.body, f"«{refusal.label}»")
        assert refusal.body == INVALID_REFRESH_TOKEN_REFUSAL, (
            f"«{refusal.label}» must answer literally {INVALID_REFRESH_TOKEN_REFUSAL}, got {refusal.body!r}"
        )

    def assert_refused_as_unified_authorization_failure(self, refusal: RefusedRotation) -> None:
        assert_unified_authorization_refusal(refusal.http_status, refusal.body)

    def assert_envelope_has_only_allowed_fields(self, refusal: RefusedRotation) -> None:
        assert_error_envelope_shape(refusal.body, f"«{refusal.label}»")

    def assert_secret_marker_is_absent(self, refusal: RefusedRotation, sentinel: SecretSentinel) -> None:
        for secret in (sentinel.marker, required_value(JWT_SECRET_VARIABLE)):
            assert secret not in refusal.raw_text, (
                f"«{refusal.label}» must not disclose the secret marker, found {secret!r} in {refusal.raw_text!r}"
            )

    def assert_carries_no_internal_details(self, refusal: RefusedRotation) -> None:
        lowered = refusal.raw_text.lower()
        leaks = [trace for trace in INTERNAL_DETAIL_TRACES if trace in lowered]
        assert not leaks, f"«{refusal.label}» must not leak internal details, found {leaks!r} in {refusal.raw_text!r}"

    @staticmethod
    def _marker() -> str:
        return f"secret-sentinel-{uuid.uuid4().hex}"
