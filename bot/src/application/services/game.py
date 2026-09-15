"""Сервис игр."""

from typing import List

from core.logger import setup_logger

from domain.entities.game import Game
from infrastructure.repositories.factory import get_game_repository, get_game_session_repository


class GameService:
    """Сервис для работы с играми."""

    def __init__(self):
        self.logger = setup_logger("GAME SERVICE")
        self.game_repo = get_game_repository()
        self.session_repo = get_game_session_repository()

    async def get_all_games(self) -> List[Game]:
        """Получить все активные игры."""
        return await self.game_repo.get_all_active()

    async def get_games_played_count(self, user_id: int) -> int:
        """Подсчитать количество сыгранных игр пользователя."""
        return await self.session_repo.count_by_user(user_id)


_service: GameService = None


def get_game_service() -> GameService:
    """Получить синглтон сервиса игр."""
    global _service
    if _service is None:
        _service = GameService()
    return _service
