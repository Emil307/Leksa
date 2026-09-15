"""Маппер топиков игр."""

from domain.entities.user_game_thread import UserGameThread
from infrastructure.database.models.user_game_thread import UserGameThreadModel
from infrastructure.repositories.mappers._base import BaseMapper


class UserGameThreadMapper(BaseMapper[UserGameThread, UserGameThreadModel]):
    """Маппер UserGameThread <-> UserGameThreadModel."""

    domain_class = UserGameThread


def get_user_game_thread_mapper() -> UserGameThreadMapper:
    return UserGameThreadMapper()
