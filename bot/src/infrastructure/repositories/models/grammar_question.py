"""Репозиторий вопросов по грамматике."""

from typing import List

from sqlalchemy import func

from domain.entities.grammar_question import GrammarQuestion
from infrastructure.database.models.grammar_question import GrammarQuestionModel
from infrastructure.repositories._base import SQLAlchemyRepository
from infrastructure.repositories.mappers.grammar_question import get_grammar_question_mapper


class GrammarQuestionRepository(SQLAlchemyRepository):
    """Репозиторий для работы с вопросами по грамматике."""

    model = GrammarQuestionModel

    def __init__(self):
        super().__init__()
        self.mapper = get_grammar_question_mapper()

    async def get_random(self, limit: int = 10, level: str = None) -> List[GrammarQuestion]:
        """Получить случайные вопросы по грамматике."""
        filters = [GrammarQuestionModel.is_active == True]

        if level:
            filters.append(GrammarQuestionModel.level == level)

        items = await self.get_all_by_filter(
            filters=filters,
            order=[func.random()],
            limit=limit,
        )
        return [self.mapper.to_domain(i) for i in items]

    async def get_all_active(self) -> List[GrammarQuestion]:
        """Получить все активные вопросы по грамматике."""
        items = await self.get_all_by_filter(
            filters=[GrammarQuestionModel.is_active == True],
        )
        return [self.mapper.to_domain(i) for i in items]
