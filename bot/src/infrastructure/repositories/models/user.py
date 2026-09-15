"""Репозиторий пользователя."""

from typing import Optional

from domain.entities.user import User, UserCreate, UserUpdate
from infrastructure.database.models.user import UserModel
from infrastructure.repositories._base import SQLAlchemyRepository, UnitOfWork
from infrastructure.repositories.mappers.user import get_user_mapper


class UserRepository(SQLAlchemyRepository):
    """Репозиторий для работы с пользователями."""

    model = UserModel

    def __init__(self, unit_of_work: Optional[UnitOfWork] = None):
        super().__init__(unit_of_work)
        self.mapper = get_user_mapper()

    async def get_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        """Получить пользователя по telegram_id."""
        model = await self.get_one(
            filters=[UserModel.telegram_id == telegram_id],
        )
        if model is None:
            return None
        return self.mapper.to_domain(model)

    async def create(self, data: UserCreate) -> Optional[User]:
        """Создать пользователя."""
        create_dict = self.mapper.build_create_dict(data)
        model = await self.add_one(create_dict)
        if model is None:
            return None
        return self.mapper.to_domain(model)

    async def update_by_telegram_id(self, telegram_id: int, data: UserUpdate) -> Optional[User]:
        """Обновить пользователя по telegram_id."""
        update_dict = self.mapper.build_update_dict(data)
        if not update_dict:
            return await self.get_by_telegram_id(telegram_id)
        model = await self.update_one(
            filters=[UserModel.telegram_id == telegram_id],
            data=update_dict,
        )
        if model is None:
            return None
        return self.mapper.to_domain(model)
