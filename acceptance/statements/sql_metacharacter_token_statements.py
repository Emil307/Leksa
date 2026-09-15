from dataclasses import dataclass

from clients.application.auth_client import AuthClient
from clients.application.dto.auth.session_dto import SessionDto
from clients.application.dto.auth.session_refusal_dto import SessionRefusalDto

from statements.auth_database import AuthDatabase
from statements.auth_statements import AuthStatements
from statements.stored_session_row import StoredSessionRow, assert_stored_row_unchanged
from statements.wire_contract import assert_unified_authorization_refusal

TAUTOLOGY_TOKEN = "' OR 1=1 --"
STACKED_STATEMENT_TOKEN = "'; UPDATE auth.t_sessions SET expires_at = now() WHERE '1'='1"


@dataclass(frozen=True)
class OwnedSession:
    email: str
    session: SessionDto
    stored: StoredSessionRow
    session_ids: list[str]


@dataclass(frozen=True)
class SeveralSessions:
    owners: tuple[OwnedSession, ...]


@dataclass(frozen=True)
class MetacharacterAttempt:
    token: str
    refusal: SessionRefusalDto
    rows_after: tuple[StoredSessionRow, ...]
    session_ids_after: tuple[list[str], ...]


class SqlMetacharacterTokenStatements:
    def __init__(self, auth_client: AuthClient, auth_statements: AuthStatements, auth_database: AuthDatabase):
        self.auth_client = auth_client
        self.auth_statements = auth_statements
        self.auth_database = auth_database

    async def given_sessions_of_several_users(self) -> SeveralSessions:
        first = await self._given_owned_session()
        second = await self._given_owned_session()
        return SeveralSessions(owners=(first, second))

    async def refresh_with_tautology_token(self, sessions: SeveralSessions) -> MetacharacterAttempt:
        return await self._refresh_with(TAUTOLOGY_TOKEN, sessions)

    async def refresh_with_stacked_statement_token(self, sessions: SeveralSessions) -> MetacharacterAttempt:
        return await self._refresh_with(STACKED_STATEMENT_TOKEN, sessions)

    def assert_refused_with_unified_authorization_error(self, attempt: MetacharacterAttempt) -> None:
        assert_unified_authorization_refusal(attempt.refusal.http_status, attempt.refusal.body)

    def assert_no_session_was_changed(self, sessions: SeveralSessions, attempt: MetacharacterAttempt) -> None:
        for owner, row_after in zip(sessions.owners, attempt.rows_after, strict=True):
            assert_stored_row_unchanged(
                owner.stored, row_after, f"the token {attempt.token!r} beside the session of {owner.email}"
            )

    def assert_no_session_was_opened_or_closed(self, sessions: SeveralSessions, attempt: MetacharacterAttempt) -> None:
        for owner, ids_after in zip(sessions.owners, attempt.session_ids_after, strict=True):
            assert ids_after == owner.session_ids, (
                f"the token {attempt.token!r} must leave the sessions of {owner.email} as {owner.session_ids!r}, "
                f"found {ids_after!r}"
            )

    async def _given_owned_session(self) -> OwnedSession:
        email = self.auth_statements.new_user_email()
        session = await self.auth_statements.given_live_session_of(email)
        stored = await self.auth_database.stored_session_row(session.session_id)
        session_ids = await self.auth_database.session_ids_of_user(session.user_id)
        return OwnedSession(email=email, session=session, stored=stored, session_ids=session_ids)

    async def _refresh_with(self, token: str, sessions: SeveralSessions) -> MetacharacterAttempt:
        refusal = await self.auth_client.refresh_session_capturing_refusal(token)
        rows_after = tuple(
            [await self.auth_database.stored_session_row(owner.session.session_id) for owner in sessions.owners]
        )
        session_ids_after = tuple(
            [await self.auth_database.session_ids_of_user(owner.session.user_id) for owner in sessions.owners]
        )
        return MetacharacterAttempt(
            token=token, refusal=refusal, rows_after=rows_after, session_ids_after=session_ids_after
        )
