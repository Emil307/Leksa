"""Исключения пользователя."""

from domain.exceptions._base import BaseDomainException, ErrorCode


class UserNotFoundException(BaseDomainException):
    """Пользователь не найден."""

    def __init__(self, message: str = "Пользователь не найден"):
        super().__init__(message, code=ErrorCode.user_not_found)


class UserAlreadyExistsException(BaseDomainException):
    """Пользователь уже существует."""

    def __init__(self, message: str = "Пользователь уже существует"):
        super().__init__(message, code=ErrorCode.user_already_exists)
