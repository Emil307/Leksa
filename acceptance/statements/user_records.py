import uuid
from dataclasses import fields, replace
from typing import Any

from clients.application.dto.profile.profile_dto import UserRecord

EMPTY_RECORD = UserRecord(**dict.fromkeys(field.name for field in fields(UserRecord)))


def user_record(**overrides: Any) -> UserRecord:
    return replace(EMPTY_RECORD, id=str(uuid.uuid4()), **overrides)
