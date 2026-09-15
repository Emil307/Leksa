from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from clients.application.dto.profile.profile_dto import ProfileDto, UserRecord
from clients.application.profile_client import ProfileClient

from statements.access_token import access_token_claims, forge_token
from statements.auth_database import AuthDatabase
from statements.profile_statements import assert_profile_of_user_returned
from statements.test_data import TestData
from statements.user_records import user_record
from statements.wire_contract import (
    ACCESS_TOKEN_LIFETIME,
    HTTP_UNAUTHORIZED,
    UNAUTHORIZED_FIELD_NAMES,
)

LIVE_SESSION = timedelta(hours=1)
SECONDS_BEFORE_TOKEN_EXPIRES = 2
ONE_SECOND = 1
ONE_MICROSECOND = timedelta(microseconds=1)
NO_TIME = timedelta(0)

ZERO_EXPIRY = 0
NEGATIVE_EXPIRY = -1
CALENDAR_CEILING_EXPIRY = 253402300800
BEYOND_EXACT_INTEGER_EXPIRY = 2**53


@dataclass(frozen=True)
class TokenUnderTest:
    user_id: str
    access_token: str


class ExpiryClockStatements:
    def __init__(self, profile_client: ProfileClient, auth_database: AuthDatabase):
        self.profile_client = profile_client
        self.auth_database = auth_database

    async def user_whose_token_is_moments_from_expiry(self) -> TokenUnderTest:
        return await self._sign_in(self._epoch_now() + SECONDS_BEFORE_TOKEN_EXPIRES, self._live_session())

    async def user_whose_token_expires_at_this_very_second(self) -> TokenUnderTest:
        return await self._sign_in(self._epoch_now(), self._live_session())

    async def user_whose_token_expired_a_second_ago(self) -> TokenUnderTest:
        return await self._sign_in(self._epoch_now() - ONE_SECOND, self._live_session())

    async def user_whose_token_expiry_is_zero(self) -> TokenUnderTest:
        return await self._sign_in(ZERO_EXPIRY, self._live_session())

    async def user_whose_token_expiry_is_negative(self) -> TokenUnderTest:
        return await self._sign_in(NEGATIVE_EXPIRY, self._live_session())

    async def user_whose_token_expiry_reaches_the_calendar_ceiling(self) -> TokenUnderTest:
        return await self._sign_in(CALENDAR_CEILING_EXPIRY, self._live_session())

    async def user_whose_token_expiry_exceeds_the_exact_integer_range(self) -> TokenUnderTest:
        return await self._sign_in(BEYOND_EXACT_INTEGER_EXPIRY, self._live_session())

    async def user_whose_session_outlives_the_request_by_a_microsecond(self) -> TokenUnderTest:
        return await self._sign_in(self._live_token(), datetime.now(UTC) + LIVE_SESSION + ONE_MICROSECOND)

    async def user_whose_session_expires_at_this_very_moment(self) -> TokenUnderTest:
        return await self._sign_in(self._live_token(), datetime.now(UTC) + NO_TIME)

    async def user_whose_session_expired_a_microsecond_ago(self) -> TokenUnderTest:
        return await self._sign_in(self._live_token(), datetime.now(UTC) - ONE_MICROSECOND)

    async def request_profile(self, subject: TokenUnderTest) -> ProfileDto:
        return await self.profile_client.fetch_profile(subject.access_token)

    def assert_profile_returned(self, profile: ProfileDto, subject: TokenUnderTest) -> None:
        assert_profile_of_user_returned(profile, subject.user_id, "a token and a session that both outlive the request")

    def assert_uniform_authorization_refusal(self, profile: ProfileDto) -> None:
        assert profile.http_status == HTTP_UNAUTHORIZED, (
            f"an expiry boundary that has been reached must answer {HTTP_UNAUTHORIZED}, got {profile.http_status}"
        )
        assert profile.field_names == UNAUTHORIZED_FIELD_NAMES, (
            f"the refusal must carry exactly {sorted(UNAUTHORIZED_FIELD_NAMES)} and no account data, "
            f"got {sorted(profile.field_names)}"
        )

    async def _sign_in(self, token_expiry: object, session_expires_at: datetime) -> TokenUnderTest:
        record = self._account_without_optional_fields()
        await self.auth_database.store_user(record)
        session_id = await self.auth_database.open_session(
            user_id=record.id,
            opened_at=session_expires_at - LIVE_SESSION,
            expires_at=session_expires_at,
        )
        return TokenUnderTest(
            user_id=record.id,
            access_token=forge_token(access_token_claims(record.id, session_id, token_expiry)),
        )

    @staticmethod
    def _live_session() -> datetime:
        return datetime.now(UTC) + LIVE_SESSION

    @classmethod
    def _live_token(cls) -> int:
        return cls._epoch_now() + int(ACCESS_TOKEN_LIFETIME.total_seconds())

    @staticmethod
    def _epoch_now() -> int:
        return int(datetime.now(UTC).timestamp())

    @staticmethod
    def _account_without_optional_fields() -> UserRecord:
        return user_record(name=TestData.unique_name("clock"), email=TestData.unique_email("clock"))
