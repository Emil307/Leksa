from dataclasses import dataclass
from typing import Any

from clients.application.auth_client import AuthClient
from clients.application.dto.auth.session_dto import SessionDto
from clients.application.dto.auth.session_refusal_dto import SessionRefusalDto

from statements.auth_database import AuthDatabase
from statements.auth_statements import AuthStatements, assert_exactly_one_session
from statements.session_refresh_statements import SessionRefreshStatements
from statements.session_row_lock import SessionRowLock
from statements.stored_session_row import StoredSessionRow, assert_stored_row_unchanged

HTTP_SERVICE_UNAVAILABLE = 503
TEMPORARY_UNAVAILABILITY: dict[str, Any] = {
    "code": "UNAVAILABLE",
    "message": "Request could not be processed",
    "payload": {},
}
SESSION_FIELD = "session"


@dataclass(frozen=True)
class SessionUnderStorageFailure:
    email: str
    session: SessionDto
    row_before: StoredSessionRow


@dataclass(frozen=True)
class FailedRotation:
    refusal: SessionRefusalDto
    row_after: StoredSessionRow
    session_ids_after: list[str]


class StorageFailureRollbackStatements:
    def __init__(
        self,
        auth_client: AuthClient,
        auth_statements: AuthStatements,
        session_refresh_statements: SessionRefreshStatements,
        auth_database: AuthDatabase,
        session_row_lock: SessionRowLock,
    ):
        self.auth_client = auth_client
        self.auth_statements = auth_statements
        self.session_refresh_statements = session_refresh_statements
        self.auth_database = auth_database
        self.session_row_lock = session_row_lock

    async def given_live_session_whose_rotation_commit_fails(self) -> SessionUnderStorageFailure:
        email = self.auth_statements.new_user_email()
        session = await self.auth_statements.given_live_session_of(email)
        row_before = await self.auth_database.stored_session_row(session.session_id)
        await self.session_row_lock.hold(session.session_id)
        return SessionUnderStorageFailure(email=email, session=session, row_before=row_before)

    async def given_live_session_that_survived_a_failed_rotation(self) -> SessionUnderStorageFailure:
        live = await self.given_live_session_whose_rotation_commit_fails()
        failed = await self.rotate_tokens_while_storage_fails(live)
        self.assert_rotation_answered_no_tokens(failed)
        self.assert_previous_token_and_expiry_are_kept_together(live, failed)
        return live

    async def rotate_tokens_while_storage_fails(self, live: SessionUnderStorageFailure) -> FailedRotation:
        refusal = await self.auth_client.refresh_session_capturing_refusal(live.session.refresh_token)
        await self.session_row_lock.release()
        row_after = await self.auth_database.stored_session_row(live.session.session_id)
        session_ids_after = await self.auth_database.session_ids_of_user(live.session.user_id)
        return FailedRotation(refusal=refusal, row_after=row_after, session_ids_after=session_ids_after)

    async def retry_with_the_old_refresh_token(self, live: SessionUnderStorageFailure) -> SessionDto:
        return await self.auth_client.refresh_session(live.session.refresh_token)

    def assert_rotation_answered_temporary_unavailability(self, failed: FailedRotation) -> None:
        assert failed.refusal.http_status == HTTP_SERVICE_UNAVAILABLE, (
            f"a storage failure during rotation must answer {HTTP_SERVICE_UNAVAILABLE}, "
            f"got {failed.refusal.http_status} with body {failed.refusal.body!r}"
        )
        assert failed.refusal.body == TEMPORARY_UNAVAILABILITY, (
            f"the temporary unavailability must be literally {TEMPORARY_UNAVAILABILITY}, got {failed.refusal.body!r}"
        )

    def assert_rotation_answered_no_tokens(self, failed: FailedRotation) -> None:
        assert not isinstance(failed.refusal.body, dict) or SESSION_FIELD not in failed.refusal.body, (
            f"a failed rotation must not answer a partially live pair, got {failed.refusal.body!r}"
        )

    def assert_previous_token_and_expiry_are_kept_together(
        self, live: SessionUnderStorageFailure, failed: FailedRotation
    ) -> None:
        assert_stored_row_unchanged(
            live.row_before, failed.row_after, f"the failed rotation of session {live.session.session_id!r}"
        )

    def assert_no_partially_live_session_row_exists(
        self, live: SessionUnderStorageFailure, failed: FailedRotation
    ) -> None:
        assert_exactly_one_session(
            failed.session_ids_after, live.session.session_id, f"the failed rotation of the session of {live.email}"
        )

    def assert_old_token_rotated_into_a_new_pair(self, live: SessionUnderStorageFailure, rotated: SessionDto) -> None:
        self.session_refresh_statements.assert_rotation_succeeded(rotated)
        self.session_refresh_statements.assert_session_identifier_is_unchanged(live.session, rotated)
        self.session_refresh_statements.assert_both_tokens_are_new(live.session, rotated)

    async def assert_stored_row_holds_the_new_pair(self, live: SessionUnderStorageFailure, rotated: SessionDto) -> None:
        row = await self.auth_database.stored_session_row(live.session.session_id)
        assert row.refresh_token == rotated.refresh_token, (
            f"the row of session {live.session.session_id!r} must store the refresh token the retry answered with, "
            "the storage holds another token"
        )
