from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ApiContractDto:
    http_status: int
    security_schemes: dict[str, Any]
    paths: dict[str, Any]
