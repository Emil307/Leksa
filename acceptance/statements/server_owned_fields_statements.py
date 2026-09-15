import uuid
from dataclasses import dataclass
from typing import Any

from clients.application.auth_client import CHALLENGE_START_PATH, CHALLENGE_VERIFY_PATH, AuthClient

from statements.auth_database import AuthDatabase
from statements.auth_statements import (
    CHALLENGE_START_RESPONSE_FIELDS,
    EMAIL_CODE,
    HTTP_OK,
    AuthStatements,
    assert_sole_email_account,
    is_canonical_uuid,
)
from statements.outbox_database import OutboxDatabase
from statements.test_data import TestData

PLANTED_EXPIRES_AT = "2099-01-01T00:00:00+00:00"
PLANTED_STATUS = "VERIFIED"
PLANTED_CODE = "000111"
PLANTED_RETRY_AFTER = 0
PLANTED_PROVIDER = "telegram"
PLANTED_NAME = "planted-name"
PLANTED_ATTEMPTS = 0
PLANTED_REMAINING = 99
PLANTED_TOKEN_PREFIX = "planted-token-"
EMPTY_NAME = ""
NO_USER = 0


@dataclass(frozen=True)
class PlantedStart:
    http_status: int
    field_names: frozenset[str]
    challenge_id: str | None
    expires_at: str | None
    email: str
    planted_challenge_id: str
    planted_uniqueness_key: str


@dataclass(frozen=True)
class PlantedVerify:
    http_status: int
    user_id: str | None
    session_id: str | None
    refresh_token: str | None
    access_token: str | None
    challenge_email: str
    planted_email: str
    planted_user_id: str
    planted_session_id: str


class ServerOwnedFieldsStatements:
    def __init__(
        self,
        auth_client: AuthClient,
        auth_statements: AuthStatements,
        auth_database: AuthDatabase,
        outbox_database: OutboxDatabase,
    ):
        self.auth_client = auth_client
        self.auth_statements = auth_statements
        self.auth_database = auth_database
        self.outbox_database = outbox_database

    async def request_code_with_server_fields(self) -> PlantedStart:
        email = self.auth_statements.new_user_email()
        planted_challenge_id = str(uuid.uuid4())
        planted_uniqueness_key = TestData.unique_email("hijacked")
        response = await self.auth_client.post(
            CHALLENGE_START_PATH,
            json={
                "email": email,
                "challengeType": EMAIL_CODE,
                "challengeId": planted_challenge_id,
                "expiresAt": PLANTED_EXPIRES_AT,
                "status": PLANTED_STATUS,
                "code": PLANTED_CODE,
                "uniquenessKey": planted_uniqueness_key,
                "retryAfterSeconds": PLANTED_RETRY_AFTER,
            },
        )
        answered = self._object(response.json())
        return PlantedStart(
            http_status=response.status_code,
            field_names=frozenset(answered),
            challenge_id=answered.get("challengeId"),
            expires_at=answered.get("expiresAt"),
            email=email,
            planted_challenge_id=planted_challenge_id,
            planted_uniqueness_key=planted_uniqueness_key,
        )

    def assert_start_answers_only_server_generated_values(self, planted: PlantedStart) -> None:
        assert planted.http_status == HTTP_OK, (
            f"a code request carrying server-owned fields must still be handled normally with {HTTP_OK}, "
            f"got {planted.http_status}"
        )
        assert planted.field_names == CHALLENGE_START_RESPONSE_FIELDS, (
            f"the answer must carry exactly {sorted(CHALLENGE_START_RESPONSE_FIELDS)}, "
            f"got {sorted(planted.field_names)}"
        )
        assert is_canonical_uuid(planted.challenge_id) and planted.challenge_id != planted.planted_challenge_id, (
            f"the planted challengeId {planted.planted_challenge_id!r} must not win over the generated one, "
            f"got {planted.challenge_id!r}"
        )
        assert planted.expires_at != PLANTED_EXPIRES_AT, (
            f"the planted expiresAt {PLANTED_EXPIRES_AT!r} must not win over the computed one"
        )

    async def assert_stored_challenge_belongs_to_the_requested_address(self, planted: PlantedStart) -> None:
        code = await self.outbox_database.queued_code_for(planted.email)
        assert code is not None, f"a login code must be queued for {planted.email}, the outbox stayed empty"
        assert code != PLANTED_CODE, f"the planted code {PLANTED_CODE!r} must not be stored as the challenge secret"
        hijack = await self.auth_client.verify_challenge(planted.planted_challenge_id, code)
        assert hijack.http_status != HTTP_OK, (
            f"the planted challengeId {planted.planted_challenge_id!r} must name no stored challenge — "
            f"verifying it must not be accepted with {HTTP_OK}"
        )
        session = await self.auth_client.verify_challenge(planted.challenge_id, code)
        self.auth_statements.assert_verify_accepted(session)
        accounts = await self.auth_database.provider_accounts_of_user(session.user_id)
        assert_sole_email_account(accounts, planted.email, "the user behind the planted code request")
        owners = await self.auth_database.count_users_with_email(planted.planted_uniqueness_key)
        assert owners == NO_USER, (
            f"the planted uniquenessKey {planted.planted_uniqueness_key!r} must own no user, found {owners}"
        )

    async def verify_code_with_server_fields(self) -> PlantedVerify:
        email = self.auth_statements.new_user_email()
        requested = await self.auth_statements.request_code_and_capture(email)
        planted_email = TestData.unique_email("hijacked")
        planted_user_id = str(uuid.uuid4())
        planted_session_id = str(uuid.uuid4())
        planted_refresh = PLANTED_TOKEN_PREFIX + uuid.uuid4().hex
        planted_access = PLANTED_TOKEN_PREFIX + uuid.uuid4().hex
        response = await self.auth_client.post(
            CHALLENGE_VERIFY_PATH,
            json={
                "challengeId": requested.challenge_id,
                "code": requested.code,
                "email": planted_email,
                "provider": PLANTED_PROVIDER,
                "providerId": planted_email,
                "userId": planted_user_id,
                "name": PLANTED_NAME,
                "sessionId": planted_session_id,
                "refreshToken": planted_refresh,
                "accessToken": planted_access,
                "attempts": PLANTED_ATTEMPTS,
                "attemptsRemaining": PLANTED_REMAINING,
            },
        )
        answered = self._object(response.json())
        session = self._object(answered.get("session"))
        return PlantedVerify(
            http_status=response.status_code,
            user_id=self._object(answered.get("user")).get("id"),
            session_id=session.get("id"),
            refresh_token=session.get("refreshToken"),
            access_token=session.get("accessToken"),
            challenge_email=email,
            planted_email=planted_email,
            planted_user_id=planted_user_id,
            planted_session_id=planted_session_id,
        )

    def assert_session_is_the_server_generated_one(self, planted: PlantedVerify) -> None:
        assert planted.http_status == HTTP_OK, (
            f"a verify request carrying server-owned fields must still be handled normally with {HTTP_OK}, "
            f"got {planted.http_status}"
        )
        assert is_canonical_uuid(planted.session_id) and planted.session_id != planted.planted_session_id, (
            f"the planted sessionId {planted.planted_session_id!r} must not win, got {planted.session_id!r}"
        )
        assert is_canonical_uuid(planted.user_id) and planted.user_id != planted.planted_user_id, (
            f"the planted userId {planted.planted_user_id!r} must not win, got {planted.user_id!r}"
        )
        issued = (planted.refresh_token, planted.access_token)
        assert all(token and not token.startswith(PLANTED_TOKEN_PREFIX) for token in issued), (
            f"the planted refreshToken and accessToken must not win, got {issued!r}"
        )

    async def assert_identity_comes_from_the_stored_challenge(self, planted: PlantedVerify) -> None:
        users = await self.auth_database.users_with_email(planted.challenge_email)
        assert users == [(planted.user_id, EMPTY_NAME)], (
            f"the identity must come from the stored challenge — {planted.challenge_email} must own exactly "
            f"{[(planted.user_id, EMPTY_NAME)]!r}, found {users!r}"
        )
        accounts = await self.auth_database.provider_accounts_of_user(planted.user_id)
        assert_sole_email_account(accounts, planted.challenge_email, "the user behind the planted verify request")
        owners = await self.auth_database.count_users_with_email(planted.planted_email)
        assert owners == NO_USER, f"the planted email {planted.planted_email!r} must own no user, found {owners}"

    @staticmethod
    def _object(value: Any) -> dict[str, Any]:
        return value if isinstance(value, dict) else {}
