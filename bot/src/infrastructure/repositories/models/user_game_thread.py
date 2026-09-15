"""Репозиторий топиков игр."""

from typing import Optional

from domain.entities.user_game_thread import UserGameThread
from infrastructure.database.models.user_game_thread import UserGameThreadModel
from infrastructure.repositories._base import SQLAlchemyRepository
from infrastructure.repositories.mappers.user_game_thread import get_user_game_thread_mapper


class UserGameThreadRepository(SQLAlchemyRepository):
    """Репозиторий для работы с топиками игр."""

    model = UserGameThreadModel

    def __init__(self):
        super().__init__()
        self.mapper = get_user_game_thread_mapper()

    async def get_thread(self, user_id: int, game_type: str) -> Optional[UserGameThread]:
        """Получить топик игры пользователя."""
        model = await self.get_one(
            filters=[
                UserGameThreadModel.user_id == user_id,
                UserGameThreadModel.game_type == game_type,
            ],
        )
        if model is None:
            return None
        return self.mapper.to_domain(model)

    async def upsert_thread(self, user_id: int, game_type: str, thread_id: int) -> Optional[UserGameThread]:
        """Создать или обновить топик игры."""
        existing = await self.get_thread(user_id, game_type)

        if existing:
            model = await self.update_one(
                filters=[
                    UserGameThreadModel.user_id == user_id,
                    UserGameThreadModel.game_type == game_type,
                ],
                data={"thread_id": thread_id},
            )
        else:
            model = await self.add_one({
                "user_id": user_id,
                "game_type": game_type,
                "thread_id": thread_id,
            })

        if model is None:
            return None
        return self.mapper.to_domain(model)
