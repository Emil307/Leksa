"""Базовый маппер для преобразования ORM -> Domain."""

from typing import Generic, TypeVar, Type, Dict, Callable, List
from dataclasses import dataclass

from pydantic import BaseModel

from core.logger import setup_logger

DomainT = TypeVar("DomainT")
OrmT = TypeVar("OrmT")


@dataclass
class RelationMapping:
    """Описание связи для маппинга."""

    field: str
    mapper_getter: Callable
    is_list: bool = False


class BaseMapper(Generic[DomainT, OrmT]):
    """Базовый маппер ORM <-> Domain."""

    domain_class: Type[DomainT]
    logger_name: str = "MAPPER"

    def _get_field_adapters(self) -> Dict[str, Callable]:
        """Адаптеры для преобразования отдельных полей."""
        return {}

    def _get_relations(self) -> List[RelationMapping]:
        """Список связей для маппинга."""
        return []

    def _build_scalar(self, model: OrmT) -> dict:
        """Построить словарь скалярных полей из ORM-модели."""
        relation_names = {r.field for r in self._get_relations()}
        relation_names |= getattr(self.domain_class, "_relation_fields", set())
        adapters = self._get_field_adapters()

        data = {}
        for key in self.domain_class.model_fields:
            if key in relation_names:
                continue
            if key in adapters:
                data[key] = adapters[key](model)
            elif hasattr(model, key):
                data[key] = getattr(model, key)
        return data

    def _build_relations(self, model: OrmT) -> dict:
        """Построить словарь связанных полей из ORM-модели."""
        data = {}
        for rel in self._get_relations():
            try:
                raw = getattr(model, rel.field, None)
                if raw is None:
                    continue
                mapper = rel.mapper_getter()
                if rel.is_list:
                    data[rel.field] = [mapper.to_domain(item) for item in raw]
                else:
                    data[rel.field] = mapper.to_domain(raw)
            except Exception:
                pass
        return data

    def to_domain(self, model: OrmT) -> DomainT:
        """Преобразовать ORM-модель в доменную сущность."""
        scalar = self._build_scalar(model)
        scalar.update(self._build_relations(model))
        return self.domain_class.model_validate(scalar)

    def build_create_dict(self, create: BaseModel) -> dict:
        """Построить словарь для создания записи."""
        return self.domain_class.build_create_dict(create)

    def build_update_dict(self, update: BaseModel) -> dict:
        """Построить словарь для обновления записи."""
        return self.domain_class.build_update_dict(update)
