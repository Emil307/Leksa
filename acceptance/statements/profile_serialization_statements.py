import uuid
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from clients.application.dto.profile.profile_dto import UserRecord
from clients.application.dto.profile.raw_profile_response import RawProfileResponse
from clients.application.profile_client import BEARER_SCHEME, ProfileClient

from statements.access_token import mint_access_token
from statements.auth_database import AuthDatabase
from statements.profile_statements import (
    ACCESS_TOKEN_LIFETIME,
    CLIENT_FIELD_NAMES,
    SESSION_LIFETIME,
    STORED_BIRTHDAY,
    STORED_CREATED_AT,
    STORED_GENDER,
    STORED_PHONE,
    STORED_UPDATED_AT,
    SignedInUser,
)
from statements.test_data import TestData
from statements.user_records import user_record
from statements.wire_contract import HTTP_OK

FOREIGN_IDENTIFIER_PARAMETER = "userId"
CONTENT_TYPE_HEADER = "content-type"
JSON_CONTENT_TYPE = "application/json"

HOSTILE_NAME = "<script>alert('xss')</script>"
HOSTILE_SURNAME = "'; DROP TABLE auth.t_users; --"
HOSTILE_CITY = 'line-one\nSet-Cookie: injected=1\r\n\t"quoted", "injectedField": 1\x1b[31m\x07'
FORGED_HEADER_NAME = "set-cookie"
FORGED_JSON_FIELD = "injectedField"


@dataclass(frozen=True)
class HostileAccounts:
    owner: SignedInUser
    other_user: UserRecord
    unknown_user_id: str


class ProfileSerializationStatements:
    def __init__(self, profile_client: ProfileClient, auth_database: AuthDatabase):
        self.profile_client = profile_client
        self.auth_database = auth_database

    async def sign_in_two_users_with_hostile_text_in_the_first_account(self) -> HostileAccounts:
        owner_record = self._account_with_hostile_text()
        other_record = self._plain_account()
        await self.auth_database.store_user(owner_record)
        await self.auth_database.store_user(other_record)

        now = datetime.now(UTC)
        owner_session = await self.auth_database.open_session(
            user_id=owner_record.id, opened_at=now, expires_at=now + SESSION_LIFETIME
        )
        await self.auth_database.open_session(user_id=other_record.id, opened_at=now, expires_at=now + SESSION_LIFETIME)

        return HostileAccounts(
            owner=SignedInUser(
                record=owner_record,
                access_token=mint_access_token(
                    user_id=owner_record.id,
                    session_id=owner_session,
                    expires_at=now + ACCESS_TOKEN_LIFETIME,
                ),
            ),
            other_user=other_record,
            unknown_user_id=str(uuid.uuid4()),
        )

    async def request_profile_for_existing_foreign_identifier(self, accounts: HostileAccounts) -> RawProfileResponse:
        return await self._request_profile(accounts.owner.access_token, accounts.other_user.id)

    async def request_profile_for_unknown_identifier(self, accounts: HostileAccounts) -> RawProfileResponse:
        return await self._request_profile(accounts.owner.access_token, accounts.unknown_user_id)

    def assert_both_responses_are_verbatim_equal(
        self, existing: RawProfileResponse, unknown: RawProfileResponse
    ) -> None:
        assert existing.http_status == unknown.http_status, (
            "a foreign identifier that exists and one that does not must be indistinguishable; "
            f"got {existing.http_status} and {unknown.http_status}"
        )
        assert existing.raw_text == unknown.raw_text, (
            "both responses must be verbatim equal, otherwise the identifier probes existence"
        )

    def assert_each_response_is_the_owners_safe_document(
        self, responses: Iterable[RawProfileResponse], accounts: HostileAccounts
    ) -> None:
        for response in responses:
            self.assert_carries_only_the_token_owner(response, accounts)
            self.assert_other_user_is_not_disclosed(response, accounts)
            self.assert_is_one_valid_json_document(response)
            self.assert_dangerous_values_are_returned_as_string_data(response, accounts)
            self.assert_created_no_header_json_field_or_query(response)

    def assert_carries_only_the_token_owner(self, response: RawProfileResponse, accounts: HostileAccounts) -> None:
        body = self._decoded_body(response)
        assert response.http_status == HTTP_OK, (
            f"the token owner must still receive {HTTP_OK}, got {response.http_status}"
        )
        assert frozenset(body) == CLIENT_FIELD_NAMES, (
            f"expected exactly {sorted(CLIENT_FIELD_NAMES)}, got {sorted(body)}"
        )
        assert body["id"] == accounts.owner.record.id, (
            "the profile must be selected by the verified subject, never by the client-sent identifier"
        )
        assert body["email"] == accounts.owner.record.email, "the profile must echo the token owner's account"

    def assert_other_user_is_not_disclosed(self, response: RawProfileResponse, accounts: HostileAccounts) -> None:
        for secret in (accounts.other_user.id, accounts.other_user.email, accounts.other_user.name):
            assert secret not in response.raw_text, (
                f"the response must not disclose the second user's data, found {secret!r}"
            )
        assert accounts.unknown_user_id not in response.raw_text, (
            "the response must not echo the client-sent identifier back"
        )

    def assert_is_one_valid_json_document(self, response: RawProfileResponse) -> None:
        content_type = response.headers.get(CONTENT_TYPE_HEADER, "")
        assert content_type.startswith(JSON_CONTENT_TYPE), f"expected a JSON document, got {content_type!r}"
        body = self._decoded_body(response)
        assert isinstance(body, dict), f"the response must be one JSON object, got {type(body).__name__}"

    def assert_dangerous_values_are_returned_as_string_data(
        self, response: RawProfileResponse, accounts: HostileAccounts
    ) -> None:
        body = self._decoded_body(response)
        for field, stored in (
            ("name", accounts.owner.record.name),
            ("surname", accounts.owner.record.surname),
            ("city", accounts.owner.record.city),
        ):
            assert isinstance(body[field], str), f"{field} must come back as string data, got {type(body[field])}"
            assert body[field] == stored, f"{field} must round-trip verbatim as data, got {body[field]!r}"

    def assert_created_no_header_json_field_or_query(self, response: RawProfileResponse) -> None:
        assert FORGED_HEADER_NAME not in response.headers, "a stored value must not create a response header"
        for value in response.headers.values():
            assert "\n" not in value and "\r" not in value, "no header value may carry a line break"
        assert FORGED_JSON_FIELD not in self._decoded_body(response), (
            "a stored value must not create a JSON field of its own"
        )

    async def _request_profile(self, access_token: str, foreign_user_id: str) -> RawProfileResponse:
        return await self.profile_client.request_profile(
            f"{BEARER_SCHEME} {access_token}",
            params={FOREIGN_IDENTIFIER_PARAMETER: foreign_user_id},
        )

    @staticmethod
    def _decoded_body(response: RawProfileResponse) -> Any:
        assert response.body is not None, "the response must stay one valid JSON document"
        return response.body

    @classmethod
    def _account_with_hostile_text(cls) -> UserRecord:
        return cls._account(HOSTILE_NAME, HOSTILE_SURNAME, HOSTILE_CITY, "hostile")

    @classmethod
    def _plain_account(cls) -> UserRecord:
        return cls._account(
            TestData.unique_name("neighbour"),
            TestData.unique_name("neighbour-surname"),
            TestData.unique_name("neighbour-city"),
            "neighbour",
        )

    @staticmethod
    def _account(name: str, surname: str, city: str, email_prefix: str) -> UserRecord:
        return user_record(
            name=name,
            surname=surname,
            email=TestData.unique_email(email_prefix),
            is_superuser=False,
            created_at=STORED_CREATED_AT,
            updated_at=STORED_UPDATED_AT,
            avatar_id=str(uuid.uuid4()),
            birthday=STORED_BIRTHDAY,
            gender=STORED_GENDER,
            city=city,
            phone=STORED_PHONE,
        )
