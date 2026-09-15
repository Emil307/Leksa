from dataclasses import dataclass
from datetime import date, datetime


@dataclass(frozen=True)
class UserRecord:
    id: str | None
    name: str | None
    surname: str | None
    email: str | None
    is_superuser: bool | None
    created_at: datetime | None
    updated_at: datetime | None
    avatar_id: str | None
    birthday: date | None
    gender: str | None
    city: str | None
    phone: str | None


@dataclass(frozen=True)
class ProfileDto:
    http_status: int
    record: UserRecord
    field_names: frozenset[str]
