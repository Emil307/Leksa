from clients.application.auth_client import AuthClient
from clients.application.dto.auth.session_dto import SessionDto

from statements.access_token import claims_of
from statements.auth_statements import AuthStatements, is_canonical_uuid
from statements.wire_contract import HTTP_OK

REFRESH_RESPONSE_FIELDS = frozenset({"session"})
ROTATED_SESSION_FIELDS = frozenset({"id", "refreshToken", "accessToken"})


class SessionRefreshStatements:
    def __init__(self, auth_client: AuthClient, auth_statements: AuthStatements):
        self.auth_client = auth_client
        self.auth_statements = auth_statements

    async def given_live_session(self) -> SessionDto:
        return await self.auth_statements.given_live_session()

    async def refresh_tokens(self, session: SessionDto) -> SessionDto:
        return await self.auth_client.refresh_session(session.refresh_token)

    def assert_rotation_succeeded(self, rotated: SessionDto) -> None:
        assert rotated.http_status == HTTP_OK, f"token refresh must answer {HTTP_OK}, got {rotated.http_status}"

    def assert_session_identifier_is_unchanged(self, session: SessionDto, rotated: SessionDto) -> None:
        assert is_canonical_uuid(rotated.session_id), (
            f"the rotated session must carry a canonical UUID id, got {rotated.session_id!r}"
        )
        assert rotated.session_id == session.session_id, (
            f"rotation must keep session id {session.session_id!r}, got {rotated.session_id!r}"
        )

    def assert_both_tokens_are_new(self, session: SessionDto, rotated: SessionDto) -> None:
        assert rotated.refresh_token, "rotation must answer with a refresh token"
        assert rotated.refresh_token != session.refresh_token, (
            "rotation must issue a new refresh token, the presented one came back unchanged"
        )
        assert rotated.access_token, "rotation must answer with an access token"
        assert claims_of(rotated.access_token)["jti"] != claims_of(session.access_token)["jti"], (
            "rotation must mint an access token with a fresh jti, the previous id came back"
        )

    def assert_only_allowed_session_fields_are_returned(self, rotated: SessionDto) -> None:
        assert rotated.response_field_names == REFRESH_RESPONSE_FIELDS, (
            f"token refresh must answer exactly {sorted(REFRESH_RESPONSE_FIELDS)}, "
            f"got {sorted(rotated.response_field_names)}"
        )
        assert rotated.session_field_names == ROTATED_SESSION_FIELDS, (
            f"the rotated session must carry exactly {sorted(ROTATED_SESSION_FIELDS)}, "
            f"got {sorted(rotated.session_field_names)}"
        )
