"""Базовые классы для доменных исключений."""

from enum import Enum
from typing import Optional, Mapping, Any


class ErrorCode(str, Enum):
    """Коды ошибок."""

    internal = "internal"
    invalid_operation = "invalid_operation"
    validation_error = "validation_error"

    # User
    user_not_found = "user_not_found"
    user_already_exists = "user_already_exists"
    user_inactive = "user_inactive"


class ActionCode(str, Enum):
    """Коды действий для обработки ошибок."""

    pass


class BaseDomainException(Exception):
    """Базовый класс для всех доменных исключений."""

    def __init__(
        self,
        message: str,
        *,
        code: Optional[ErrorCode] = None,
        action_code: Optional[ActionCode] = None,
        payload: Mapping[str, Any] | None = None,
        log_level: str = "error",
        expose_to_user: bool = True,
    ):
        self.message = message
        self.code = code
        self.action_code = action_code
        self.payload = payload
        self.log_level = log_level
        self.expose_to_user = expose_to_user
        super().__init__(self.message)

    def __str__(self) -> str:
        return self.message


class InternalServerErrorException(BaseDomainException):
    """Внутренняя ошибка сервера."""

    pass


class InvalidOperationException(BaseDomainException):
    """Операция не может быть выполнена."""

    pass
