from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any

from clients.application.auth_client import AuthClient
from clients.application.dto.auth.session_refusal_dto import SessionRefusalDto

from statements.auth_database import AuthDatabase
from statements.session_refresh_statements import SessionRefreshStatements
from statements.session_rotation_consistency_statements import LiveStoredSession
from statements.stored_session_row import assert_stored_row_unchanged
from statements.wire_contract import (
    MAX_TOKEN_BYTES,
    REFRESH_TOKEN_INVALID_MESSAGE,
    assert_validation_refusal,
    validation_refusal,
)

UNREADABLE_REQUEST_MESSAGE = "Request could not be processed"
TOKEN_REQUIRED_MESSAGE = "Refresh token is required"

TOKEN_FIELD = "refreshToken"
PLAIN_TEXT = "text/plain"
NOT_JSON = b"this is not json"
JSON_TEXT_TOKEN = b'"plain-string-instead-of-object"'
JSON_ARRAY = b'["refreshToken"]'
CONTROL_CHARACTER = "\x01"
TAB = "\t"
MULTIBYTE_TOKEN = "токен"
ASCII_FILLER = "a"


@dataclass(frozen=True)
class InvalidRefreshRequest:
    label: str
    expected_message: str
    send: Callable[[], Awaitable[SessionRefusalDto]]


class RefreshRequestValidationStatements:
    def __init__(
        self,
        auth_client: AuthClient,
        session_refresh_statements: SessionRefreshStatements,
        auth_database: AuthDatabase,
    ):
        self.auth_client = auth_client
        self.session_refresh_statements = session_refresh_statements
        self.auth_database = auth_database

    def requests_without_a_valid_json_body(self) -> list[InvalidRefreshRequest]:
        return [
            self._unreadable("тело отсутствует", self.auth_client.refresh_without_a_body),
            self._unreadable(
                "тело не является JSON", lambda: self.auth_client.refresh_with_raw_body(NOT_JSON, "application/json")
            ),
            self._unreadable(
                "тело — JSON-строка, а не объект",
                lambda: self.auth_client.refresh_with_raw_body(JSON_TEXT_TOKEN, "application/json"),
            ),
            self._unreadable(
                "тело — JSON-массив, а не объект",
                lambda: self.auth_client.refresh_with_raw_body(JSON_ARRAY, "application/json"),
            ),
            self._unreadable(
                "тело отправлено как text/plain", lambda: self.auth_client.refresh_with_raw_body(NOT_JSON, PLAIN_TEXT)
            ),
        ]

    def requests_with_a_missing_null_or_empty_token(self) -> list[InvalidRefreshRequest]:
        return [
            self._required("поле refreshToken отсутствует", {}),
            self._required("refreshToken равен null", {TOKEN_FIELD: None}),
            self._required("refreshToken — пустая строка", {TOKEN_FIELD: ""}),
            self._required("refreshToken — строка из пробелов", {TOKEN_FIELD: "   "}),
            self._required("refreshToken — число, а не строка", {TOKEN_FIELD: 12345}),
        ]

    def requests_with_an_ill_formed_token(self, live: LiveStoredSession) -> list[InvalidRefreshRequest]:
        token = live.session.refresh_token
        return [
            self._invalid("refreshToken содержит управляющий символ", token + CONTROL_CHARACTER),
            self._invalid("refreshToken содержит табуляцию", token + TAB),
            self._invalid("refreshToken содержит многобайтовые символы", MULTIBYTE_TOKEN),
            self._invalid("refreshToken длиннее 512 байт", ASCII_FILLER * (MAX_TOKEN_BYTES + 1)),
            self._invalid("refreshToken из 512 символов, но длиннее 512 байт", MULTIBYTE_TOKEN[0] * MAX_TOKEN_BYTES),
        ]

    async def send_each_and_assert_validation_error(self, attempts: list[InvalidRefreshRequest]) -> None:
        for attempt in attempts:
            refusal = await attempt.send()
            self._assert_validation_error(attempt, refusal)

    async def assert_session_row_is_unchanged(self, live: LiveStoredSession) -> None:
        stored_after = await self.auth_database.stored_session_row(live.session.session_id)
        assert_stored_row_unchanged(
            live.stored, stored_after, f"the refused requests of session {live.session.session_id!r}"
        )

    async def assert_live_refresh_token_still_rotates(self, live: LiveStoredSession) -> None:
        rotated = await self.session_refresh_statements.refresh_tokens(live.session)
        self.session_refresh_statements.assert_rotation_succeeded(rotated)
        self.session_refresh_statements.assert_session_identifier_is_unchanged(live.session, rotated)
        self.session_refresh_statements.assert_both_tokens_are_new(live.session, rotated)

    def _unreadable(self, label: str, send: Callable[[], Awaitable[SessionRefusalDto]]) -> InvalidRefreshRequest:
        return InvalidRefreshRequest(label, UNREADABLE_REQUEST_MESSAGE, send)

    def _required(self, label: str, body: dict[str, Any]) -> InvalidRefreshRequest:
        return InvalidRefreshRequest(
            label, TOKEN_REQUIRED_MESSAGE, lambda: self.auth_client.refresh_with_json_body(body)
        )

    def _invalid(self, label: str, token: str) -> InvalidRefreshRequest:
        return InvalidRefreshRequest(
            label, REFRESH_TOKEN_INVALID_MESSAGE, lambda: self.auth_client.refresh_with_json_body({TOKEN_FIELD: token})
        )

    @staticmethod
    def _assert_validation_error(attempt: InvalidRefreshRequest, refusal: SessionRefusalDto) -> None:
        expected = validation_refusal(attempt.expected_message)
        assert_validation_refusal(refusal.http_status, refusal.body, f"«{attempt.label}»")
        assert refusal.body == expected, f"«{attempt.label}» must answer literally {expected!r}, got {refusal.body!r}"
