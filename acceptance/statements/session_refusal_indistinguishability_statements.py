import json
import secrets
from dataclasses import dataclass
from datetime import UTC, datetime

from clients.application.auth_client import AuthClient
from clients.application.dto.auth.session_refusal_dto import SessionRefusalDto

from statements.auth_database import AuthDatabase
from statements.auth_statements import AuthStatements, assert_exactly_one_session
from statements.stored_session_row import StoredSessionRow, assert_stored_row_unchanged
from statements.test_data import TestData
from statements.user_records import user_record
from statements.wire_contract import SESSION_LIFETIME, assert_error_envelope_shape, assert_unified_authorization_refusal

ABSENT_TOKEN_BYTES = 32


@dataclass(frozen=True)
class PreparedTokens:
    user_id: str
    email: str
    session_id: str
    inaccessible_token: str
    absent_token: str
    row_before: StoredSessionRow


@dataclass(frozen=True)
class RefusalPair:
    inaccessible: SessionRefusalDto
    absent: SessionRefusalDto
    row_after: StoredSessionRow
    session_ids_after: list[str]


class SessionRefusalIndistinguishabilityStatements:
    def __init__(self, auth_client: AuthClient, auth_statements: AuthStatements, auth_database: AuthDatabase):
        self.auth_client = auth_client
        self.auth_statements = auth_statements
        self.auth_database = auth_database

    async def given_expired_session_and_absent_token(self) -> PreparedTokens:
        record = user_record(name=TestData.unique_name("expired"), email=TestData.unique_email("expired"))
        await self.auth_database.store_user(record)
        now = datetime.now(UTC)
        session_id = await self.auth_database.open_session(
            user_id=record.id, opened_at=now - SESSION_LIFETIME, expires_at=now
        )
        row = await self.auth_database.stored_session_row(session_id)
        assert row.expires_at <= datetime.now(UTC), (
            f"the prepared session {session_id!r} must already be expired, "
            f"its expiry {row.expires_at.isoformat()} lies ahead"
        )
        return self._prepared(record.id, record.email, session_id, row.refresh_token, row)

    async def given_used_token_and_absent_token(self) -> PreparedTokens:
        email = self.auth_statements.new_user_email()
        session = await self.auth_statements.given_live_session_of(email)
        rotated = await self.auth_client.refresh_session(session.refresh_token)
        assert rotated.refresh_token and rotated.refresh_token != session.refresh_token, (
            f"the preparing rotation of session {session.session_id!r} must replace the refresh token, it did not"
        )
        row = await self.auth_database.stored_session_row(session.session_id)
        return self._prepared(session.user_id, email, session.session_id, session.refresh_token, row)

    @staticmethod
    def _prepared(
        user_id: str, email: str, session_id: str, inaccessible_token: str, row: StoredSessionRow
    ) -> PreparedTokens:
        absent_token = secrets.token_urlsafe(ABSENT_TOKEN_BYTES)
        assert absent_token != inaccessible_token, "the absent token must differ from the inaccessible one"
        return PreparedTokens(
            user_id=user_id,
            email=email,
            session_id=session_id,
            inaccessible_token=inaccessible_token,
            absent_token=absent_token,
            row_before=row,
        )

    async def refresh_with_each_token(self, prepared: PreparedTokens) -> RefusalPair:
        inaccessible = await self.auth_client.refresh_session_capturing_refusal(prepared.inaccessible_token)
        absent = await self.auth_client.refresh_session_capturing_refusal(prepared.absent_token)
        row_after = await self.auth_database.stored_session_row(prepared.session_id)
        session_ids_after = await self.auth_database.session_ids_of_user(prepared.user_id)
        return RefusalPair(
            inaccessible=inaccessible, absent=absent, row_after=row_after, session_ids_after=session_ids_after
        )

    def assert_both_refusals_are_the_unified_authorization_refusal(self, pair: RefusalPair) -> None:
        assert_unified_authorization_refusal(pair.inaccessible.http_status, pair.inaccessible.body)
        assert_unified_authorization_refusal(pair.absent.http_status, pair.absent.body)

    def assert_refusals_are_identical(self, pair: RefusalPair) -> None:
        assert pair.inaccessible.http_status == pair.absent.http_status, (
            f"the inaccessible session must be refused with the same status as the absent one, "
            f"got {pair.inaccessible.http_status} versus {pair.absent.http_status}"
        )
        assert pair.inaccessible.body == pair.absent.body, (
            f"the inaccessible session must be refused with the same code, message and payload as the absent one, "
            f"got {pair.inaccessible.body!r} versus {pair.absent.body!r}"
        )

    def assert_refusals_reveal_neither_owner_nor_existence(self, prepared: PreparedTokens, pair: RefusalPair) -> None:
        for name, refusal in (("inaccessible", pair.inaccessible), ("absent", pair.absent)):
            assert_error_envelope_shape(refusal.body, f"the refusal of the {name} token")
            serialized = json.dumps(refusal.body)
            for label, secret in self._identifying_values(prepared):
                assert secret not in serialized, (
                    f"the refusal of the {name} token must not reveal the {label}, found it in {serialized!r}"
                )

    @staticmethod
    def _identifying_values(prepared: PreparedTokens) -> list[tuple[str, str]]:
        return [
            ("owner id", prepared.user_id),
            ("owner email", prepared.email),
            ("session id", prepared.session_id),
            ("inaccessible token", prepared.inaccessible_token),
            ("absent token", prepared.absent_token),
        ]

    def assert_no_session_was_changed(self, prepared: PreparedTokens, pair: RefusalPair) -> None:
        assert_stored_row_unchanged(
            prepared.row_before, pair.row_after, f"neither refused request of session {prepared.session_id!r}"
        )
        assert_exactly_one_session(
            pair.session_ids_after, prepared.session_id, f"refusing both tokens for the user {prepared.email}"
        )
