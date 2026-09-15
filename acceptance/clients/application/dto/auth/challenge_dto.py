from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class ChallengeStartDto:
    http_status: int
    challenge_id: str | None
    challenge_type: str | None
    expires_at: datetime | None
    field_names: frozenset[str]
    requested_at: datetime
    responded_at: datetime
