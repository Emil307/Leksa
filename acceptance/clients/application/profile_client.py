from datetime import date, datetime
from typing import Any

from httpx import Response

from clients.application.application_client import ApplicationClient
from clients.application.dto.profile.profile_dto import ProfileDto, UserRecord
from clients.application.dto.profile.raw_profile_response import RawProfileResponse

PROFILE_PATH = "/api/v1/profile"

AUTHORIZATION_HEADER = "Authorization"
BEARER_SCHEME = "Bearer"

UTC_SUFFIX = "Z"
UTC_OFFSET = "+00:00"


class ProfileClient(ApplicationClient):
    async def fetch_profile(self, access_token: str, params: dict[str, str] | None = None) -> ProfileDto:
        response = await self.request_profile(f"{BEARER_SCHEME} {access_token}", params=params)

        return ProfileDto(
            http_status=response.http_status,
            record=self._user_record(response.object_body),
            field_names=response.field_names,
        )

    async def request_profile(
        self,
        authorization: str | bytes | None = None,
        extra_headers: dict[str, str] | None = None,
        params: dict[str, str] | None = None,
    ) -> RawProfileResponse:
        headers: dict[Any, Any] = {} if authorization is None else {AUTHORIZATION_HEADER: authorization}
        headers |= extra_headers or {}

        response = await self.get(PROFILE_PATH, headers=headers, params=params)

        return self._captured(response)

    @classmethod
    def _captured(cls, response: Response) -> RawProfileResponse:
        return RawProfileResponse(
            http_status=response.status_code,
            raw_body=response.content,
            raw_text=response.text,
            body=cls._json_body(response),
            headers={name.lower(): value for name, value in response.headers.items()},
        )

    @classmethod
    def _user_record(cls, body: dict[str, Any]) -> UserRecord:
        return UserRecord(
            id=body.get("id"),
            name=body.get("name"),
            surname=body.get("surname"),
            email=body.get("email"),
            is_superuser=body.get("isSuperuser"),
            created_at=cls._parse_instant(body.get("createdAt")),
            updated_at=cls._parse_instant(body.get("updatedAt")),
            avatar_id=body.get("avatarId"),
            birthday=cls._parse_calendar_date(body.get("birthday")),
            gender=body.get("gender"),
            city=body.get("city"),
            phone=body.get("phone"),
        )

    @staticmethod
    def _parse_instant(raw: Any) -> Any:
        if not isinstance(raw, str):
            return raw
        try:
            return datetime.fromisoformat(raw.replace(UTC_SUFFIX, UTC_OFFSET))
        except ValueError:
            return raw

    @staticmethod
    def _parse_calendar_date(raw: Any) -> Any:
        if not isinstance(raw, str):
            return raw
        try:
            return date.fromisoformat(raw)
        except ValueError:
            return raw
