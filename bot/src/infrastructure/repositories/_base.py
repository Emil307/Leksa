"""Базовый класс для репозиториев."""

from contextlib import asynccontextmanager
from typing import Any, Dict, List, Type, Optional

from sqlalchemy import func, select, insert, update, delete, Table
from sqlalchemy.ext.asyncio import AsyncSession

from core.logger import setup_logger

from domain.exceptions import (
    ErrorCode,
    InternalServerErrorException,
)

from infrastructure.database.base import get_session


class UnitOfWork:
    """Unit of Work для управления транзакциями."""

    def __init__(self):
        self.logger = setup_logger("UNIT OF WORK", "DEBUG")
        self._session: Optional[AsyncSession] = None

    @asynccontextmanager
    async def __call__(self):
        """Контекстный менеджер для работы с сессией."""
        session_gen = get_session()
        session = await session_gen.__anext__()
        self._session = session
        try:
            yield self
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            self._session = None
            try:
                await session_gen.__anext__()
            except StopAsyncIteration:
                pass

    @property
    def session(self) -> AsyncSession:
        """Получить текущую сессию."""
        if self._session is None:
            raise InternalServerErrorException(
                "Session is not initialized. Use UnitOfWork as a context manager.",
                code=ErrorCode.internal,
            )
        return self._session


class SQLAlchemyRepository:
    """Базовый класс для всех репозиториев."""

    model: Type[Table] = None

    def __init__(self, unit_of_work: Optional[UnitOfWork] = None):
        self._uow = unit_of_work or UnitOfWork()
        self.logger = setup_logger(f"SQL REPOSITORY ({self.model.__name__})", "DEBUG")

    async def get_one(self, filters: List, selectin_loads: List = None) -> Optional[Any]:
        """Получить один объект с фильтрами."""
        try:
            async with self._uow() as uow:
                stmt = select(self.model).filter(*filters)
                if selectin_loads:
                    stmt = stmt.options(*selectin_loads)
                res = await uow.session.execute(stmt)
                return res.scalar_one_or_none()
        except Exception as e:
            self.logger.error(f"[GET ONE] [{self.model}] Error: {e}")
            return None

    async def add_one(self, data: Dict) -> Optional[Any]:
        """Добавить один объект."""
        try:
            async with self._uow() as uow:
                stmt = insert(self.model).values(data).returning(self.model)
                res = await uow.session.execute(stmt)
                return res.scalar_one_or_none()
        except Exception as e:
            self.logger.error(f"[ADD ONE] [{self.model}] Error: {e}")
            return None

    async def update_one(self, filters: List, data: Dict) -> Optional[Any]:
        """Обновить один объект."""
        try:
            async with self._uow() as uow:
                stmt = update(self.model).filter(*filters).values(data).returning(self.model)
                res = await uow.session.execute(stmt)
                return res.scalar_one_or_none()
        except Exception as e:
            self.logger.error(f"[UPD ONE] [{self.model}] Error: {e}")
            return None

    async def get_all_by_filter(
        self,
        filters: List = None,
        selectin_loads: List = None,
        order: List = None,
        limit: int = None,
        offset: int = None,
    ) -> List[Any]:
        """Получить объекты по фильтру."""
        try:
            async with self._uow() as uow:
                stmt = select(self.model)
                if filters:
                    stmt = stmt.filter(*filters)
                if order:
                    stmt = stmt.order_by(*order)
                if selectin_loads:
                    stmt = stmt.options(*selectin_loads)
                if limit:
                    stmt = stmt.limit(limit)
                if offset:
                    stmt = stmt.offset(offset)
                res = await uow.session.execute(stmt)
                return res.scalars().all()
        except Exception as e:
            self.logger.error(f"[GET ALL FILTER] [{self.model}] Error: {e}")
            return []

    async def get_paginated_by_filter(
        self,
        filters: List = None,
        order: List = None,
        limit: int = None,
        offset: int = None,
    ) -> tuple[List[Any], int]:
        """Получить объекты с пагинацией и общим количеством."""
        try:
            async with self._uow() as uow:
                # Подсчёт общего количества
                count_stmt = select(func.count(self.model.id))
                if filters:
                    count_stmt = count_stmt.filter(*filters)
                total = (await uow.session.execute(count_stmt)).scalar() or 0

                # Получение записей
                stmt = select(self.model)
                if filters:
                    stmt = stmt.filter(*filters)
                if order:
                    stmt = stmt.order_by(*order)
                if limit:
                    stmt = stmt.limit(limit)
                if offset:
                    stmt = stmt.offset(offset)
                res = await uow.session.execute(stmt)
                return res.scalars().all(), total
        except Exception as e:
            self.logger.error(f"[GET PAGINATED] [{self.model}] Error: {e}")
            return [], 0

    async def count_by_filter(self, filters: List = None) -> int:
        """Подсчитать количество объектов по фильтру."""
        try:
            async with self._uow() as uow:
                stmt = select(func.count(self.model.id))
                if filters:
                    stmt = stmt.filter(*filters)
                res = await uow.session.execute(stmt)
                return res.scalar() or 0
        except Exception as e:
            self.logger.error(f"[COUNT] [{self.model}] Error: {e}")
            return 0
