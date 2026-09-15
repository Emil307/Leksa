from datetime import datetime
from typing import AsyncGenerator

from sqlalchemy import MetaData, DateTime
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Mapped, mapped_column

from core.config import get_settings


class TimestampMixin:
    """
    Миксин для добавления полей created_at и updated_at
    """
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


Base: DeclarativeMeta = declarative_base()
metadata = MetaData()

engine = None
async_session_maker = None

async def init_database():
    """Инициализация базы данных"""
    global engine, async_session_maker

    settings = get_settings()

    engine = create_async_engine(
        url=settings.db.url,
        echo=settings.debug,
        pool_pre_ping=True,
        pool_recycle=300,
    )
    
    async_session_maker = sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Получить сессию базы данных"""

    if async_session_maker is None:
        await init_database()

    async with async_session_maker() as session:
        yield session

async def close_database():
    """Закрыть подключение к базе данных"""
    if engine:
        await engine.dispose()