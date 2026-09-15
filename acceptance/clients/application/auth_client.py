from datetime import UTC, datetime
from typing import Any

from httpx import Response

from clients.application.application_client import ApplicationClient
from clients.application.dto.auth.challenge_dto import ChallengeStartDto
from clients.application.dto.auth.session_dto import SessionDto
from clients.application.dto.auth.session_refresh_outcome_dto import SessionRefreshOutcomeDto
from clients.application.dto.auth.session_refusal_dto import SessionRefusalDto

CHALLENGE_START_PATH = "/api/v1/auth/challenge/start"
CHALLENGE_VERIFY_PATH = "/api/v1/auth/challenge/verify"
TOKEN_REFRESH_PATH = "/api/v1/auth/token/refresh"

OWNER_FIELD = "userId"
CONTENT_TYPE_HEADER = "Content-Type"
JSON_CONTENT_TYPE = "application/json"

UTC_SUFFIX = "Z"
UTC_OFFSET = "+00:00"


class AuthClient(ApplicationClient):
    async def start_challenge(self, email: str, challenge_type: str) -> ChallengeStartDto:
        requested_at = datetime.now(UTC)
        response = await self.post(CHALLENGE_START_PATH, json={"email": email, "challengeType": challenge_type})
        responded_at = datetime.now(UTC)
        return self._challenge_of(response, requested_at, responded_at)

    async def verify_challenge(self, challenge_id: str, code: str) -> SessionDto:
        return self._session_of(
            await self.post(CHALLENGE_VERIFY_PATH, json={"challengeId": challenge_id, "code": code})
        )

    async def refresh_session(self, refresh_token: str) -> SessionDto:
        return self._session_of(await self._post_refresh(refresh_token))

    async def refresh_session_capturing_refusal(self, refresh_token: str) -> SessionRefusalDto:
        return self._refusal_of(await self._post_refresh(refresh_token))

    async def refresh_session_naming_owner(self, refresh_token: str, owner_user_id: str) -> SessionRefusalDto:
        return await self.refresh_with_json_body({"refreshToken": refresh_token, OWNER_FIELD: owner_user_id})

    async def refresh_with_json_body(self, body: Any) -> SessionRefusalDto:
        return self._refusal_of(await self.post(TOKEN_REFRESH_PATH, json=body))

    async def refresh_without_a_body(self) -> SessionRefusalDto:
        return await self.refresh_with_raw_body(b"", JSON_CONTENT_TYPE)

    async def refresh_with_raw_body(self, content: bytes, content_type: str) -> SessionRefusalDto:
        response = await self.post(TOKEN_REFRESH_PATH, content=content, headers={CONTENT_TYPE_HEADER: content_type})
        return self._refusal_of(response)

    async def refresh_session_capturing_outcome(self, refresh_token: str) -> SessionRefreshOutcomeDto:
        response = await self._post_refresh(refresh_token)
        return SessionRefreshOutcomeDto(session=self._session_of(response), body=self._json_body(response))

    async def _post_refresh(self, refresh_token: str) -> Response:
        return await self.post(TOKEN_REFRESH_PATH, json={"refreshToken": refresh_token})

    def _refusal_of(self, response: Response) -> SessionRefusalDto:
        return SessionRefusalDto(
            http_status=response.status_code, body=self._json_body(response), raw_text=response.text
        )

    def _challenge_of(self, response: Response, requested_at: datetime, responded_at: datetime) -> ChallengeStartDto:
        body = self._json_object(response)
        return ChallengeStartDto(
            http_status=response.status_code,
            challenge_id=body.get("challengeId"),
            challenge_type=body.get("challengeType"),
            expires_at=self._parse_timestamp(body.get("expiresAt")),
            field_names=frozenset(body),
            requested_at=requested_at,
            responded_at=responded_at,
        )

    def _session_of(self, response: Response) -> SessionDto:
        body = self._json_object(response)
        session = self._nested_object(body, "session")
        user = self._nested_object(body, "user")
        return SessionDto(
            http_status=response.status_code,
            user_id=user.get("id"),
            session_id=session.get("id"),
            refresh_token=session.get("refreshToken"),
            access_token=session.get("accessToken"),
            response_field_names=frozenset(body),
            session_field_names=frozenset(session),
        )

    @staticmethod
    def _parse_timestamp(raw: Any) -> datetime | None:
        if not isinstance(raw, str):
            return None
        try:
            return datetime.fromisoformat(raw.replace(UTC_SUFFIX, UTC_OFFSET))
        except ValueError:
            return None
