from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class SessionRefusalDto:
    http_status: int
    body: Any
    raw_text: str
