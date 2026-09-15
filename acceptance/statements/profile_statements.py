import uuid
from dataclasses import dataclass
from datetime import UTC, date, datetime

from clients.application.dto.profile.profile_dto import ProfileDto, UserRecord
from clients.application.profile_client import ProfileClient

from statements.access_token import mint_access_token
from statements.auth_database import AuthDatabase
from statements.test_data import TestData
from statements.user_records import user_record
from statements.wire_contract import ACCESS_TOKEN_LIFETIME, HTTP_OK, SESSION_LIFETIME

STORED_CREATED_AT = datetime(2026, 3, 14, 9, 26, 53, tzinfo=UTC)
STORED_UPDATED_AT = datetime(2026, 5, 9, 11, 22, 33, tzinfo=UTC)
STORED_BIRTHDAY = date(1993, 7, 21)
STORED_GENDER = "female"
STORED_PHONE = "+79995550101"

CLIENT_FIELD_NAMES = frozenset(
    {
        "id",
        "name",
        "surname",
        "email",
        "isSuperuser",
        "createdAt",
        "updatedAt",
        "avatarId",
        "birthday",
        "gender",
        "city",
        "phone",
    }
)


def assert_profile_of_user_returned(profile: ProfileDto, user_id: str | None, subject: str) -> None:
    assert profile.http_status == HTTP_OK, f"{subject} must answer {HTTP_OK}, got {profile.http_status}"
    assert profile.record.id == user_id, (
        f"the profile answered to {subject} must belong to the user {user_id!r}, got {profile.record.id!r}"
    )


@dataclass(frozen=True)
class SignedInUser:
    record: UserRecord
    access_token: str


class ProfileStatements:
    def __init__(self, profile_client: ProfileClient, auth_database: AuthDatabase):
        self.profile_client = profile_client
        self.auth_database = auth_database

    async def sign_in_user_with_every_field_filled(self) -> SignedInUser:
        record = self._account_with_every_field_filled()
        await self.auth_database.store_user(record)

        now = datetime.now(UTC)
        session_id = await self.auth_database.open_session(
            user_id=record.id,
            opened_at=now,
            expires_at=now + SESSION_LIFETIME,
        )

        return SignedInUser(
            record=record,
            access_token=mint_access_token(
                user_id=record.id,
                session_id=session_id,
                expires_at=now + ACCESS_TOKEN_LIFETIME,
            ),
        )

    async def request_own_profile(self, user: SignedInUser) -> ProfileDto:
        return await self.profile_client.fetch_profile(user.access_token)

    def assert_request_succeeded(self, profile: ProfileDto) -> None:
        assert profile.http_status == HTTP_OK, (
            f"a live session and a valid access token must answer {HTTP_OK}, got {profile.http_status}"
        )

    def assert_carries_every_client_field_name(self, profile: ProfileDto) -> None:
        self._assert_body_is_exactly_the_client_fields(
            profile, "the profile must carry every account property in client naming"
        )

    def assert_values_match_stored_record(self, profile: ProfileDto, user: SignedInUser) -> None:
        assert profile.record == user.record, "the profile must echo the stored account exactly"

    def assert_response_is_not_wrapped_in_envelope(self, profile: ProfileDto) -> None:
        self._assert_body_is_exactly_the_client_fields(
            profile, "the account must sit at the root of the response, not inside an envelope"
        )

    def assert_response_carries_no_session_token_or_learner_data(self, profile: ProfileDto) -> None:
        self._assert_body_is_exactly_the_client_fields(
            profile, "the profile must not carry session, token or learner data"
        )

    @staticmethod
    def _assert_body_is_exactly_the_client_fields(profile: ProfileDto, requirement: str) -> None:
        assert profile.field_names == CLIENT_FIELD_NAMES, (
            f"{requirement}; expected exactly {sorted(CLIENT_FIELD_NAMES)}, got {sorted(profile.field_names)}"
        )

    @staticmethod
    def _account_with_every_field_filled() -> UserRecord:
        return user_record(
            name=TestData.unique_name("name"),
            surname=TestData.unique_name("surname"),
            email=TestData.unique_email("profile"),
            is_superuser=True,
            created_at=STORED_CREATED_AT,
            updated_at=STORED_UPDATED_AT,
            avatar_id=str(uuid.uuid4()),
            birthday=STORED_BIRTHDAY,
            gender=STORED_GENDER,
            city=TestData.unique_name("city"),
            phone=STORED_PHONE,
        )
