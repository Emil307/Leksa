"""Маппер идиом."""

from domain.entities.idiom import Idiom
from infrastructure.database.models.idiom import IdiomModel
from infrastructure.repositories.mappers._base import BaseMapper


class IdiomMapper(BaseMapper[Idiom, IdiomModel]):
    """Маппер Idiom <-> IdiomModel."""

    domain_class = Idiom


def get_idiom_mapper() -> IdiomMapper:
    """Получить экземпляр маппера идиом."""
    return IdiomMapper()
