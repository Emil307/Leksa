"""Мапперы игр."""

from domain.entities.game import Game, GameSession
from infrastructure.database.models.game import GameModel
from infrastructure.database.models.game_session import GameSessionModel
from infrastructure.repositories.mappers._base import BaseMapper


class GameMapper(BaseMapper[Game, GameModel]):
    """Маппер Game <-> GameModel."""

    domain_class = Game


class GameSessionMapper(BaseMapper[GameSession, GameSessionModel]):
    """Маппер GameSession <-> GameSessionModel."""

    domain_class = GameSession


def get_game_mapper() -> GameMapper:
    """Получить экземпляр маппера игр."""
    return GameMapper()


def get_game_session_mapper() -> GameSessionMapper:
    """Получить экземпляр маппера игровых сессий."""
    return GameSessionMapper()
