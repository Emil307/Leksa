import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from clients.application.auth_client import AuthClient
from clients.application.dto.auth.session_refusal_dto import SessionRefusalDto

from statements.auth_database import AuthDatabase
from statements.auth_statements import AuthStatements, assert_exactly_one_session
from statements.stored_session_row import StoredSessionRow, assert_stored_row_unchanged
from statements.wire_contract import SESSION_LIFETIME, assert_unified_authorization_refusal

EXPIRED_TOKEN = "the expired refresh token"
UNKNOWN_TOKEN = "the unknown refresh token"
USED_TOKEN = "the already used refresh token"
TOKEN_FIELD_NAMES = ("accessToken", "refreshToken", "session")


@dataclass(frozen=True)
class OwnedSession:
    user_id: str
    session_id: str
    row: StoredSessionRow


@dataclass(frozen=True)
class InvalidRefreshTokens:
    expired: str
    unknown: str
    used: str
    expired_session: OwnedSession
    used_session: OwnedSession

    def in_order(self) -> list[tuple[str, str]]:
        return [(EXPIRED_TOKEN, self.expired), (UNKNOWN_TOKEN, self.unknown), (USED_TOKEN, self.used)]


@dataclass(frozen=True)
class RefusalRound:
    refusals: list[tuple[str, SessionRefusalDto]]
    expired_after: OwnedSession
    used_after: OwnedSession
    session_ids_of_expired_user: list[str]
    session_ids_of_used_user: list[str]


class IndistinguishableRefreshRefusalStatements:
    def __init__(
        self,
        auth_client: AuthClient,
        auth_statements: AuthStatements,
        auth_database: AuthDatabase,
    ):
        self.auth_client = auth_client
        self.auth_statements = auth_statements
        self.auth_database = auth_database

    async def given_expired_unknown_and_used_refresh_tokens(self) -> InvalidRefreshTokens:
        expired_session = await self._given_expired_session()
        used_session, used_token = await self._given_session_whose_token_was_already_used()
        return InvalidRefreshTokens(
            expired=expired_session.row.refresh_token,
            unknown=uuid.uuid4().hex,
            used=used_token,
            expired_session=expired_session,
            used_session=used_session,
        )

    async def _given_expired_session(self) -> OwnedSession:
        live = await self.auth_statements.given_live_session()
        expired_at = datetime.now(UTC) - timedelta(hours=1)
        session_id = await self.auth_database.open_session(
            user_id=live.user_id, opened_at=expired_at - SESSION_LIFETIME, expires_at=expired_at
        )
        return await self._owned_session(live.user_id, session_id)

    async def _given_session_whose_token_was_already_used(self) -> tuple[OwnedSession, str]:
        live = await self.auth_statements.given_live_session()
        rotated = await self.auth_client.refresh_session(live.refresh_token)
        assert rotated.refresh_token and rotated.refresh_token != live.refresh_token, (
            f"the preparing rotation must consume {live.refresh_token!r} and answer a new token, got {rotated!r}"
        )
        return await self._owned_session(live.user_id, live.session_id), live.refresh_token

    async def _owned_session(self, user_id: str, session_id: str) -> OwnedSession:
        row = await self.auth_database.stored_session_row(session_id)
        return OwnedSession(user_id=user_id, session_id=session_id, row=row)

    async def request_refresh_with_each_token_in_turn(self, tokens: InvalidRefreshTokens) -> RefusalRound:
        refusals = [
            (label, await self.auth_client.refresh_session_capturing_refusal(token))
            for label, token in tokens.in_order()
        ]
        return RefusalRound(
            refusals=refusals,
            expired_after=await self._owned_session(tokens.expired_session.user_id, tokens.expired_session.session_id),
            used_after=await self._owned_session(tokens.used_session.user_id, tokens.used_session.session_id),
            session_ids_of_expired_user=await self.auth_database.session_ids_of_user(tokens.expired_session.user_id),
            session_ids_of_used_user=await self.auth_database.session_ids_of_user(tokens.used_session.user_id),
        )

    def assert_every_refusal_is_the_unified_authorization_refusal(self, round_: RefusalRound) -> None:
        for _, refusal in round_.refusals:
            assert_unified_authorization_refusal(refusal.http_status, refusal.body)

    def assert_status_and_envelope_bytes_are_identical(self, round_: RefusalRound) -> None:
        reference_label, reference = round_.refusals[0]
        for label, refusal in round_.refusals[1:]:
            assert refusal.http_status == reference.http_status, (
                f"{label} must answer the same status as {reference_label}, "
                f"got {refusal.http_status} against {reference.http_status}"
            )
            assert refusal.raw_text == reference.raw_text, (
                f"{label} must answer byte-for-byte the same envelope as {reference_label}, "
                f"got {refusal.raw_text!r} against {reference.raw_text!r}"
            )

    def assert_no_session_was_changed(self, tokens: InvalidRefreshTokens, round_: RefusalRound) -> None:
        assert_stored_row_unchanged(
            tokens.expired_session.row, round_.expired_after.row, "the refusals of the expired session"
        )
        assert_stored_row_unchanged(
            tokens.used_session.row, round_.used_after.row, "the refusals of the already rotated session"
        )
        assert_exactly_one_session(
            round_.session_ids_of_used_user, tokens.used_session.session_id, "refusing the used refresh token"
        )
        assert len(round_.session_ids_of_expired_user) == 2, (
            f"refusing the expired refresh token must leave the user's two sessions in storage, "
            f"found {round_.session_ids_of_expired_user!r}"
        )

    def assert_no_refusal_issued_a_token_pair(self, round_: RefusalRound) -> None:
        for label, refusal in round_.refusals:
            for field_name in TOKEN_FIELD_NAMES:
                assert field_name not in refusal.raw_text, (
                    f"{label} must not issue a token pair, the refusal carries {field_name!r}: {refusal.raw_text!r}"
                )
