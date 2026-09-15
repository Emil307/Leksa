"""Сервис управления топиками игр."""

from typing import Optional

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest

from core.logger import setup_logger

from infrastructure.repositories.factory import get_user_game_thread_repository


# Названия топиков по типам игр
GAME_THREAD_NAMES: dict[str, str] = {
    "idioms": "🎭 Идиомус",
    "grammar": "📝 Грамматикус",
    "cards": "🃏 Карточки",
}


class GameThreadService:
    """Управление Forum Topics для игр."""

    def __init__(self):
        self.logger = setup_logger("GAME THREAD SERVICE")
        self.repo = get_user_game_thread_repository()

    async def get_or_create_thread(
        self,
        bot: Bot,
        chat_id: int,
        user_id: int,
        game_type: str,
    ) -> Optional[int]:
        """
        Получить или создать топик для игры.

        Стратегия проверки: отправляем тестовое сообщение в топик
        и сравниваем message_thread_id в ответе.
        Если не совпадает — топик удалён, пересоздаём.
        """
        thread = await self.repo.get_thread(user_id=user_id, game_type=game_type)

        if thread:
            is_alive = await self._check_thread_alive(bot, chat_id, thread.thread_id)

            if is_alive:
                return thread.thread_id

            self.logger.info(
                f"Thread {thread.thread_id} deleted/invalid, recreating for user {user_id}"
            )

        return await self._create_thread(bot, chat_id, user_id, game_type)

    async def _check_thread_alive(
        self,
        bot: Bot,
        chat_id: int,
        thread_id: int,
    ) -> bool:
        """
        Проверить что топик ещё жив.

        Отправляем сообщение с message_thread_id и проверяем,
        что в ответе message_thread_id совпадает.
        Если Telegram проигнорировал thread_id (отправил в General) — топик мёртв.
        """
        try:
            sent = await bot.send_message(
                chat_id=chat_id,
                message_thread_id=thread_id,
                text="🎮",
            )

            self.logger.info(
                f"Thread check: sent.message_thread_id={sent.message_thread_id}, "
                f"expected={thread_id}"
            )

            # Удаляем тестовое сообщение
            try:
                await bot.delete_message(chat_id=chat_id, message_id=sent.message_id)
            except Exception:
                pass

            # Если message_thread_id совпадает — топик жив
            if sent.message_thread_id == thread_id:
                return True

            # Telegram отправил в General/другой топик — наш удалён
            self.logger.info(
                f"Thread {thread_id} is dead: "
                f"sent to {sent.message_thread_id} instead"
            )
            return False

        except TelegramBadRequest as e:
            self.logger.info(f"Thread {thread_id} check TelegramBadRequest: {e}")
            return False
        except Exception as e:
            self.logger.warning(f"Thread {thread_id} check error: {e}")
            return True

    async def _create_thread(
        self,
        bot: Bot,
        chat_id: int,
        user_id: int,
        game_type: str,
    ) -> Optional[int]:
        """Создать новый Forum Topic."""
        name = GAME_THREAD_NAMES.get(game_type, f"🎮 {game_type}")

        try:
            topic = await bot.create_forum_topic(
                chat_id=chat_id,
                name=name,
            )
            thread_id = topic.message_thread_id

            await self.repo.upsert_thread(
                user_id=user_id,
                game_type=game_type,
                thread_id=thread_id,
            )

            self.logger.info(f"Created thread {thread_id} ({game_type}) for user {user_id}")
            return thread_id

        except Exception as e:
            self.logger.error(f"Failed to create thread: {e}")
            return None


_service: Optional[GameThreadService] = None


def get_game_thread_service() -> GameThreadService:
    """Получить синглтон GameThreadService."""
    global _service
    if _service is None:
        _service = GameThreadService()
    return _service
