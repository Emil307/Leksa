import uuid
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta

from clients.application.dto.profile.profile_dto import UserRecord
from clients.application.dto.profile.raw_profile_response import RawProfileResponse
from clients.application.profile_client import ProfileClient

from statements.access_token import (
    JWT_SECRET_VARIABLE,
    access_token_claims,
    claims_of,
    forge_token,
    mint_access_token,
    required_value,
    token_with_tampered_signature,
)
from statements.auth_database import AuthDatabase
from statements.test_data import TestData
from statements.user_records import user_record
from statements.wire_contract import (
    ACCESS_TOKEN_LIFETIME,
    SESSION_LIFETIME,
    assert_unified_authorization_refusal,
)

EXPIRED_BY = timedelta(minutes=30)

MARKER_METACHARACTERS = "\n\r\t\x07"
UNPARSABLE_HEADER = "Token not-a-bearer-credential"
FOREIGN_AUDIENCE = "some-other-api"

INTERNAL_DETAIL_TRACES = (
    "traceback",
    "sqlalchemy",
    "asyncpg",
    "select ",
    "insert ",
    "constraint",
    "exception",
    ".py",
    "/backend/",
)
PROFILE_FIELD_TRACES = ("email", "isSuperuser", "avatarId", "birthday")


@dataclass(frozen=True)
class MarkedUser:
    record: UserRecord
    access_token: str
    markers: tuple[str, ...]


def _marked(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:12]}{MARKER_METACHARACTERS}"


def _identity(marked_value: str) -> str:
    return marked_value.rstrip(MARKER_METACHARACTERS)


def _markers_of(record: UserRecord) -> tuple[str, ...]:
    return tuple(_identity(value) for value in (record.name, record.surname, record.city))


class AuthFailureDiagnosticsStatements:
    def __init__(self, profile_client: ProfileClient, auth_database: AuthDatabase):
        self.profile_client = profile_client
        self.auth_database = auth_database

    async def sign_in_user_with_marked_personal_data(self) -> MarkedUser:
        return await self._sign_in(session_lifetime=SESSION_LIFETIME, store_account=True)

    async def sign_in_user_whose_session_has_expired(self) -> MarkedUser:
        return await self._sign_in(session_lifetime=-EXPIRED_BY, store_account=True)

    async def sign_in_user_whose_account_is_absent(self) -> MarkedUser:
        return await self._sign_in(session_lifetime=SESSION_LIFETIME, store_account=False)

    async def request_profile_with_unparsable_header(self) -> RawProfileResponse:
        return await self._request(UNPARSABLE_HEADER)

    async def request_profile_with_tampered_signature(self, user: MarkedUser) -> RawProfileResponse:
        return await self._request(f"Bearer {token_with_tampered_signature(user.access_token)}")

    async def request_profile_with_foreign_audience(self, user: MarkedUser) -> RawProfileResponse:
        return await self._request(f"Bearer {self._token_for(user, audience=FOREIGN_AUDIENCE)}")

    async def request_profile_with_valid_token(self, user: MarkedUser) -> RawProfileResponse:
        return await self._request(f"Bearer {user.access_token}")

    def assert_refusal_is_safe(self, attempt: RawProfileResponse, user: MarkedUser) -> None:
        self.assert_single_unauthorized_refusal(attempt)
        self.assert_hides_secrets_and_personal_data(attempt, user)
        self.assert_carries_no_internal_details(attempt)
        self.assert_profile_is_not_returned(attempt)

    def assert_single_unauthorized_refusal(self, attempt: RawProfileResponse) -> None:
        assert_unified_authorization_refusal(attempt.http_status, attempt.body)

    def assert_hides_secrets_and_personal_data(self, attempt: RawProfileResponse, user: MarkedUser) -> None:
        for secret in (*user.markers, user.access_token, required_value(JWT_SECRET_VARIABLE)):
            assert secret not in attempt.raw_text, (
                f"the refusal must not disclose credentials or personal data, found {secret!r} in {attempt.raw_text!r}"
            )

    def assert_carries_no_internal_details(self, attempt: RawProfileResponse) -> None:
        body = attempt.raw_text.lower()
        for trace in INTERNAL_DETAIL_TRACES:
            assert trace not in body, f"the refusal must not leak internal details, found {trace!r} in {body!r}"

    def assert_profile_is_not_returned(self, attempt: RawProfileResponse) -> None:
        for field in PROFILE_FIELD_TRACES:
            assert field not in attempt.raw_text, (
                f"a refused request must return no profile data, found {field!r} in {attempt.raw_text!r}"
            )

    async def _request(self, header_value: str) -> RawProfileResponse:
        return await self.profile_client.request_profile(header_value)

    async def _sign_in(self, session_lifetime: timedelta, store_account: bool) -> MarkedUser:
        record = self._marked_account()
        if store_account:
            await self.auth_database.store_user(record)

        now = datetime.now(UTC)
        session_id = await self.auth_database.open_session(
            user_id=record.id,
            opened_at=now - SESSION_LIFETIME,
            expires_at=now + session_lifetime,
        )
        access_token = mint_access_token(
            user_id=record.id,
            session_id=session_id,
            expires_at=now + ACCESS_TOKEN_LIFETIME,
        )
        return MarkedUser(record=record, access_token=access_token, markers=_markers_of(record))

    def _token_for(self, user: MarkedUser, audience: str) -> str:
        claims = access_token_claims(
            user.record.id,
            claims_of(user.access_token)["sid"],
            int((datetime.now(UTC) + ACCESS_TOKEN_LIFETIME).timestamp()),
        )
        return forge_token(claims | {"aud": audience})

    @staticmethod
    def _marked_account() -> UserRecord:
        return user_record(
            name=_marked("pii-name"),
            surname=_marked("pii-surname"),
            email=TestData.unique_email("auth-failure"),
            is_superuser=False,
            created_at=datetime(2026, 1, 2, 3, 4, 5, tzinfo=UTC),
            updated_at=datetime(2026, 2, 3, 4, 5, 6, tzinfo=UTC),
            avatar_id=str(uuid.uuid4()),
            birthday=date(1990, 1, 1),
            gender="male",
            city=_marked("pii-city"),
            phone="+79995550202",
        )
