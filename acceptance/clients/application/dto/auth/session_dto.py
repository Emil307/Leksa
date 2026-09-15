from dataclasses import dataclass


@dataclass(frozen=True)
class SessionDto:
    http_status: int
    user_id: str | None
    session_id: str | None
    refresh_token: str | None
    access_token: str | None
    response_field_names: frozenset[str]
    session_field_names: frozenset[str]
