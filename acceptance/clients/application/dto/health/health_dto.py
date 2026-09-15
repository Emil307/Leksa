from dataclasses import dataclass


@dataclass(frozen=True)
class HealthDto:
    http_status: int
    status: str
    database: str
