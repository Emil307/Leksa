"""Сервис вопросов по грамматике."""

from typing import List

from core.logger import setup_logger

from domain.entities.grammar_question import GrammarQuestion
from infrastructure.repositories.factory import get_grammar_question_repository


class GrammarQuestionService:
    """Сервис для работы с вопросами по грамматике."""

    def __init__(self):
        self.logger = setup_logger("GRAMMAR QUESTION SERVICE")
        self.repo = get_grammar_question_repository()

    async def get_random_questions(self, count: int = 10, level: str = None) -> List[GrammarQuestion]:
        """Получить случайные вопросы по грамматике."""
        return await self.repo.get_random(limit=count, level=level)


_service: GrammarQuestionService = None


def get_grammar_question_service() -> GrammarQuestionService:
    """Получить синглтон сервиса вопросов по грамматике."""
    global _service
    if _service is None:
        _service = GrammarQuestionService()
    return _service
