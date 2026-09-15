import json
import unicodedata
from dataclasses import dataclass
from datetime import UTC, date, datetime

from clients.application.dto.profile.profile_dto import UserRecord
from clients.application.dto.profile.raw_profile_response import RawProfileResponse
from clients.application.profile_client import BEARER_SCHEME, ProfileClient

from statements.access_token import mint_access_token
from statements.auth_database import AuthDatabase
from statements.test_data import TestData
from statements.user_records import user_record
from statements.wire_contract import ACCESS_TOKEN_LIFETIME, HTTP_OK, SESSION_LIFETIME

HOSTILE_HEADERS = {"Accept-Language": "tr-TR,ar-SA;q=0.9", "X-Timezone": "Pacific/Kiritimati"}

NULLABLE_CLIENT_FIELDS = (
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
)

PRECOMPOSED_NAME = "Zoë Ёжик 東京 🌍"
COMBINING_SURNAME = unicodedata.normalize("NFD", "Zoë Ёжик")
METACHARACTER_CITY = 'O\'Brien "quoted" \\slash\\ <script>alert(1)</script> %s {0} ;--'

DAY_EDGE_CREATED_AT = datetime(2026, 1, 1, 0, 30, 0, 123456, tzinfo=UTC)
DAY_EDGE_UPDATED_AT = datetime(2026, 12, 31, 23, 45, 15, tzinfo=UTC)
STORED_BIRTHDAY = date(2000, 1, 1)

UTC_SUFFIX = "Z"
UTC_OFFSET = "+00:00"


@dataclass(frozen=True)
class SignedInAccount:
    record: UserRecord
    access_token: str


class ProfileFieldFidelityStatements:
    def __init__(self, profile_client: ProfileClient, auth_database: AuthDatabase):
        self.profile_client = profile_client
        self.auth_database = auth_database

    async def sign_in_user_with_every_nullable_field_empty(self) -> SignedInAccount:
        return await self._sign_in(user_record(name=TestData.unique_name("name")))

    async def sign_in_user_with_multibyte_combining_and_metacharacter_text(self) -> SignedInAccount:
        return await self._sign_in(
            user_record(
                name=PRECOMPOSED_NAME,
                surname=COMBINING_SURNAME,
                city=METACHARACTER_CITY,
                email=TestData.unique_email("fidelity"),
            )
        )

    async def sign_in_user_with_day_edge_moments(self) -> SignedInAccount:
        return await self._sign_in(
            user_record(
                name=TestData.unique_name("name"),
                created_at=DAY_EDGE_CREATED_AT,
                updated_at=DAY_EDGE_UPDATED_AT,
                birthday=STORED_BIRTHDAY,
            )
        )

    async def request_own_profile_from_hostile_locale_and_timezone(
        self, account: SignedInAccount
    ) -> RawProfileResponse:
        return await self.profile_client.request_profile(
            f"{BEARER_SCHEME} {account.access_token}",
            extra_headers=HOSTILE_HEADERS,
        )

    def assert_request_succeeded(self, response: RawProfileResponse) -> None:
        assert response.http_status == HTTP_OK, (
            f"a live session and a valid access token must answer {HTTP_OK}, "
            f"got {response.http_status} with body {response.raw_body!r}"
        )

    def assert_every_unfilled_field_is_null(self, response: RawProfileResponse) -> None:
        for field in NULLABLE_CLIENT_FIELDS:
            assert field in response.object_body, (
                f"an unfilled account still owes the property {field}, got {sorted(response.object_body)}"
            )
            assert response.object_body[field] is None, (
                f"the unfilled property {field} must be JSON null, got {response.object_body[field]!r}"
            )

    def assert_text_is_returned_byte_exact(self, response: RawProfileResponse, account: SignedInAccount) -> None:
        for field, stored in (
            ("name", account.record.name),
            ("surname", account.record.surname),
            ("city", account.record.city),
        ):
            assert response.object_body[field] == stored, (
                f"{field} must come back byte-exact without normalization; "
                f"stored {stored!r}, got {response.object_body[field]!r}"
            )
        returned_surname = response.object_body["surname"]
        assert unicodedata.normalize("NFC", returned_surname) != returned_surname, (
            f"the combining form must survive the read unnormalized, got {returned_surname!r}"
        )

    def assert_body_is_valid_utf8_json(self, response: RawProfileResponse) -> None:
        try:
            decoded = response.raw_body.decode("utf-8")
        except UnicodeDecodeError as error:
            raise AssertionError(f"the response body must be valid UTF-8, got {response.raw_body!r}") from error
        assert isinstance(json.loads(decoded), dict), f"the response body must be a JSON object, got {decoded!r}"

    def assert_instants_are_in_utc(self, response: RawProfileResponse, account: SignedInAccount) -> None:
        for field, stored in (
            ("createdAt", account.record.created_at),
            ("updatedAt", account.record.updated_at),
        ):
            raw = response.object_body[field]
            assert isinstance(raw, str) and (raw.endswith(UTC_SUFFIX) or raw.endswith(UTC_OFFSET)), (
                f"{field} must be rendered in UTC regardless of the caller's locale and timezone, got {raw!r}"
            )
            assert datetime.fromisoformat(raw.replace(UTC_SUFFIX, UTC_OFFSET)) == stored, (
                f"{field} must echo the stored moment, stored {stored!r}, got {raw!r}"
            )

    def assert_birthday_is_a_calendar_date(self, response: RawProfileResponse, account: SignedInAccount) -> None:
        raw = response.object_body["birthday"]
        assert raw == account.record.birthday.isoformat(), (
            f"birthday must stay a calendar date without time or offset, "
            f"stored {account.record.birthday!r}, got {raw!r}"
        )

    async def _sign_in(self, record: UserRecord) -> SignedInAccount:
        await self.auth_database.store_user(record)
        now = datetime.now(UTC)
        session_id = await self.auth_database.open_session(
            user_id=record.id,
            opened_at=now,
            expires_at=now + SESSION_LIFETIME,
        )
        return SignedInAccount(
            record=record,
            access_token=mint_access_token(
                user_id=record.id,
                session_id=session_id,
                expires_at=now + ACCESS_TOKEN_LIFETIME,
            ),
        )
