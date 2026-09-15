from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class StoredSessionRow:
    refresh_token: str
    created_at: datetime
    expires_at: datetime


def assert_stored_row_unchanged(before: StoredSessionRow, after: StoredSessionRow, subject: str) -> None:
    assert after == before, f"{subject} must not touch the session row, stored {before!r} became {after!r}"
