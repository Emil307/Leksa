from dataclasses import dataclass
from typing import Any

from clients.application.dto.auth.session_dto import SessionDto


@dataclass(frozen=True)
class SessionRefreshOutcomeDto:
    session: SessionDto
    body: Any
