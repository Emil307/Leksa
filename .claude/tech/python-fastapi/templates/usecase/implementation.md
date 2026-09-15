# Service (Usecase) Implementation Template — python-fastapi

> Universal rules: `.claude/templates/tdd/green-usecase.md`

## Rules

- Implement the **minimal** code to pass the failing test — tests are READ-ONLY in GREEN.
- Service lives in `backend/usecase/src/services/{name}.py`, exposed via a `get_{name}_service()` cached factory.
- The service orchestrates ONE operation. It calls ports (repositories injected through `__init__`), applies domain rules, returns domain entities.
- Do NOT call another service from a service (usecases don't compose). Shared logic → a domain method or a stateless helper.
- Raise `BaseDomainException` subclasses (with `ErrorCode`) for business errors; let them bubble to the REST exception handler.
- No FastAPI and no SQLAlchemy imports in this layer — ports are `Protocol` classes.

## Shape

```python
class TaskService:
    def __init__(self, task_repository: TaskRepositoryPort, clock: Clock):
        self.task_repository = task_repository
        self.clock = clock

    async def create_task(self, request: TaskCreate) -> Task:
        existing = await self.task_repository.get_by_title(request.title)
        if existing is not None:
            raise DuplicateTaskException(request.title)
        return await self.task_repository.create(request)
```

## Reference

- Service example: `backend/usecase/src/services/user.py`
- Ports: `backend/usecase/src/ports/`
- Factory pattern: bottom of the service module (`_instance` singleton + `get_user_service()`)

## Verify

- `pytest backend/usecase/tests/services/test_{service}.py -k TestClass` is GREEN.
- File ≤ 200 lines (`wc -l`). Split by operation if larger.
