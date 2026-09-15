from collections.abc import Sequence
from dataclasses import dataclass
from datetime import UTC, datetime

from clients.application.application_client import resolve_base_url
from clients.application.dto.profile.profile_dto import ProfileDto, UserRecord
from clients.application.profile_client import ProfileClient
from httpx import AsyncClient

from statements.access_token import mint_access_token
from statements.auth_database import AuthDatabase
from statements.test_data import TestData
from statements.user_records import EMPTY_RECORD, user_record
from statements.wire_contract import (
    ACCESS_TOKEN_LIFETIME,
    HTTP_OK,
    HTTP_UNAUTHORIZED,
    REQUEST_TIMEOUT_SECONDS,
    SESSION_LIFETIME,
    UNAUTHORIZED_FIELD_NAMES,
)

APPLICATION_INSTANCES = 2


@dataclass(frozen=True)
class WarmedToken:
    record: UserRecord
    session_id: str
    access_token: str


class SessionRecheckStatements:
    def __init__(self, auth_database: AuthDatabase):
        self.instances = APPLICATION_INSTANCES
        self.auth_database = auth_database
        self._http: list[AsyncClient] = []
        self._profile_clients: list[ProfileClient] = []

    async def open(self) -> None:
        for _ in range(self.instances):
            http = AsyncClient(base_url=resolve_base_url(), timeout=REQUEST_TIMEOUT_SECONDS)
            self._http.append(http)
            self._profile_clients.append(ProfileClient(http))

    async def close(self) -> None:
        for http in self._http:
            await http.aclose()
        self._http.clear()
        self._profile_clients.clear()

    async def warm_token_through_every_instance(self) -> WarmedToken:
        warmed = await self._sign_in_user()

        for index, client in enumerate(self._profile_clients):
            profile = await client.fetch_profile(warmed.access_token)
            assert profile.http_status == HTTP_OK, (
                f"instance {index} must accept the live session before it is deactivated, got {profile.http_status}"
            )

        return warmed

    async def deactivate_session_in_postgres(self, warmed: WarmedToken) -> None:
        outcome = await self.auth_database.delete_session(warmed.session_id)
        assert outcome == "DELETE 1", f"the session row must be gone from PostgreSQL, got {outcome}"

    async def request_profile_from_every_warmed_instance(self, warmed: WarmedToken) -> list[ProfileDto]:
        return [await client.fetch_profile(warmed.access_token) for client in self._profile_clients]

    def assert_every_request_rejected_as_failed_authorization(self, profiles: Sequence[ProfileDto]) -> None:
        assert len(profiles) == self.instances, (
            f"every one of the {self.instances} warmed instances must answer, got {len(profiles)}"
        )
        for index, profile in enumerate(profiles):
            assert profile.http_status == HTTP_UNAUTHORIZED, (
                f"instance {index} must re-read the session on this request and answer "
                f"{HTTP_UNAUTHORIZED}, got {profile.http_status}"
            )
            assert profile.field_names == UNAUTHORIZED_FIELD_NAMES, (
                f"instance {index} must answer the single authorization refusal; expected "
                f"{sorted(UNAUTHORIZED_FIELD_NAMES)}, got {sorted(profile.field_names)}"
            )

    def assert_no_earlier_positive_decision_granted_access(self, profiles: Sequence[ProfileDto]) -> None:
        for index, profile in enumerate(profiles):
            assert profile.record == EMPTY_RECORD, (
                f"instance {index} must not serve account data from an earlier positive decision, got {profile.record}"
            )

    async def _sign_in_user(self) -> WarmedToken:
        record = self._account()
        await self.auth_database.store_user(record)

        now = datetime.now(UTC)
        session_id = await self.auth_database.open_session(
            user_id=record.id,
            opened_at=now,
            expires_at=now + SESSION_LIFETIME,
        )

        return WarmedToken(
            record=record,
            session_id=session_id,
            access_token=mint_access_token(
                user_id=record.id,
                session_id=session_id,
                expires_at=now + ACCESS_TOKEN_LIFETIME,
            ),
        )

    @staticmethod
    def _account() -> UserRecord:
        return user_record(
            name=TestData.unique_name("name"),
            surname=TestData.unique_name("surname"),
            email=TestData.unique_email("recheck"),
            is_superuser=False,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
