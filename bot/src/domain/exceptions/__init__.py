"""Доменные исключения."""

from domain.exceptions._base import (
    ErrorCode,
    ActionCode,
    BaseDomainException,
    InternalServerErrorException,
    InvalidOperationException,
)
from domain.exceptions.user import (
    UserNotFoundException,
    UserAlreadyExistsException,
)

__all__ = [
    "ErrorCode",
    "ActionCode",
    "BaseDomainException",
    "InternalServerErrorException",
    "InvalidOperationException",
    "UserNotFoundException",
    "UserAlreadyExistsException",
]
