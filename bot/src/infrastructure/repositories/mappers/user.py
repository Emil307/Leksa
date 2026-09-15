"""Маппер пользователя."""

from domain.entities.user import User
from infrastructure.database.models.user import UserModel
from infrastructure.repositories.mappers._base import BaseMapper


class UserMapper(BaseMapper[User, UserModel]):
    """Маппер User <-> UserModel."""

    domain_class = User
    logger_name = "USER MAPPER"


def get_user_mapper() -> UserMapper:
    """Получить экземпляр маппера пользователя."""
    return UserMapper()
