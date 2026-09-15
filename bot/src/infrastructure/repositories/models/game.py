"""Репозитории игр."""

from typing import List, Optional

from domain.entities.game import Game, GameSession
from infrastructure.database.models.game import GameModel
from infrastructure.database.models.game_session import GameSessionModel
from infrastructure.repositories._base import SQLAlchemyRepository
from infrastructure.repositories.mappers.game import get_game_mapper, get_game_session_mapper


class GameRepository(SQLAlchemyRepository):
    """Репозиторий для работы с играми."""

    model = GameModel

    def __init__(self):
        super().__init__()
        self.mapper = get_game_mapper()

    async def get_all_active(self) -> List[Game]:
        """Получить все активные игры."""
        items = await self.get_all_by_filter(
            filters=[GameModel.is_active == True],
            order=[GameModel.order.asc()],
        )
        return [self.mapper.to_domain(i) for i in items]


class GameSessionRepository(SQLAlchemyRepository):
    """Репозиторий для работы с игровыми сессиями."""

    model = GameSessionModel

    def __init__(self):
        super().__init__()
        self.mapper = get_game_session_mapper()

    async def create(self, data: dict) -> Optional[GameSession]:
        """Создать игровую сессию."""
        item = await self.add_one(data)
        return self.mapper.to_domain(item) if item else None

    async def count_by_user(self, user_id: int) -> int:
        """Подсчитать количество сессий пользователя."""
        return await self.count_by_filter(filters=[GameSessionModel.user_id == user_id])
