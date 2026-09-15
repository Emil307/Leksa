"""Маппер вопросов по грамматике."""

from domain.entities.grammar_question import GrammarQuestion
from infrastructure.database.models.grammar_question import GrammarQuestionModel
from infrastructure.repositories.mappers._base import BaseMapper


class GrammarQuestionMapper(BaseMapper[GrammarQuestion, GrammarQuestionModel]):
    """Маппер GrammarQuestion <-> GrammarQuestionModel."""

    domain_class = GrammarQuestion


def get_grammar_question_mapper() -> GrammarQuestionMapper:
    """Получить экземпляр маппера вопросов по грамматике."""
    return GrammarQuestionMapper()
