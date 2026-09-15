from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class RawProfileResponse:
    http_status: int
    raw_body: bytes
    raw_text: str
    body: Any
    headers: dict[str, str]

    @property
    def object_body(self) -> dict[str, Any]:
        return self.body if isinstance(self.body, dict) else {}

    @property
    def field_names(self) -> frozenset[str]:
        return frozenset(self.object_body)
