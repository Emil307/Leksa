# Storage (Repository) Implementation Template — python-fastapi

## Rules

- Implement minimal code to pass the failing repository test (tests READ-ONLY in GREEN).
- Repository: `class XRepository(SQLAlchemyRepository)` with `model = XModel`, obtained via a `get_x_repository()` factory, implementing the port `Protocol` declared in `backend/usecase/src/ports/`.
- Never expose `XModel` outside the repository — convert with the mapper (`to_domain()`).
- Build queries with `select(...).where(...)` and the base helpers (`get_one`, `add_one`, `update_one`); no raw row-dict grouping.
- Writes go through `UnitOfWork` (the base already wraps them). New columns → edit `XModel` AND generate an Alembic migration.

## Shape

```python
class TaskRepository(SQLAlchemyRepository):
    model = TaskModel

    def __init__(self, unit_of_work: Optional[UnitOfWork] = None):
        super().__init__(unit_of_work)
        self.mapper = get_task_mapper()

    async def get_by_id(self, task_id: UUID) -> Optional[Task]:
        model = await self.get_one(filters=[TaskModel.id == task_id])
        return self.mapper.to_domain(model) if model else None
```

## Migration (GREEN only)

- `alembic revision --autogenerate -m "add X"` then `alembic upgrade head`. Review the generated file before committing.

## Reference

- `backend/adapters/storage/src/repositories/user.py`, `repositories/_base.py`, `models/user.py`, `mappers/user.py`

## Verify

- `pytest backend/adapters/storage/tests/repositories/test_{entity}_repository.py` GREEN. File ≤ 200 lines.
