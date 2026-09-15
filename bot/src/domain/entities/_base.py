"""Базовые утилиты для доменных сущностей."""

from typing import ClassVar, Set, Union, get_origin, get_args

from pydantic import BaseModel, ConfigDict


def _unwrap_optional(annotation: type) -> type:
    """Optional[X] / Union[X, None] -> X."""
    origin = get_origin(annotation)

    if origin is Union:
        args = [a for a in get_args(annotation) if a is not type(None)]
        if len(args) == 1:
            return args[0]

    return annotation


class DomainEntity(BaseModel):
    """Базовый класс для доменных сущностей на Pydantic."""

    _relation_fields: ClassVar[Set[str]] = set()

    model_config = ConfigDict(from_attributes=True)

    def to_model_dict(self) -> dict:
        """Словарь для INSERT в БД (exclude_none + без связей)."""
        data = self.model_dump(
            exclude_none=True,
            exclude=self._relation_fields,
        )

        for k in list(data.keys()):
            attr = getattr(self, k, None)
            if isinstance(attr, BaseModel):
                data[k] = attr.model_dump(mode="json", exclude_none=True, by_alias=True)

        return data

    @classmethod
    def build_create_dict(cls, create: BaseModel) -> dict:
        """Построить словарь для создания записи."""
        entity = cls.model_validate(create.model_dump(by_alias=True))
        return entity.to_model_dict()

    @classmethod
    def build_update_dict(cls, update: BaseModel) -> dict:
        """Построить словарь для обновления записи."""
        raw = update.model_dump(exclude_unset=True, by_alias=True)
        data = {}

        for k, v in raw.items():
            if k not in cls.model_fields or k in cls._relation_fields:
                continue

            if isinstance(v, dict):
                field_type = _unwrap_optional(cls.model_fields[k].annotation)
                if isinstance(field_type, type) and issubclass(field_type, BaseModel):
                    data[k] = field_type.model_validate(v).model_dump(mode="json", by_alias=True)
                    continue

            data[k] = v

        return data

    def update(self, update: BaseModel) -> "DomainEntity":
        """Обновить сущность данными из update-модели."""
        set_keys = update.model_dump(exclude_unset=True).keys()
        if not set_keys:
            return self

        patch = {k: getattr(update, k) for k in set_keys}
        return self.model_copy(update=patch)
