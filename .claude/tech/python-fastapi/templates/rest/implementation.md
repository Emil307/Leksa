# REST (FastAPI router) Implementation Template — python-fastapi

> Universal rules: `.claude/templates/tdd/green-rest.md`

## Rules

- Minimal code to pass the failing router test (tests READ-ONLY in GREEN).
- Router in `backend/adapters/rest/src/routers/{resource}.py`; `APIRouter` included by the app factory.
- Parse the request into a Pydantic request model, call ONE service, return a Pydantic response model or `JSONResponse(content, status_code=...)`.
- No business logic in the router — delegate to the service. No try/except-and-swallow: let `BaseDomainException` bubble to `@app.exception_handler`.
- A router must not call another router; it delegates to a service.

## Shape

```python
router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: UUID, service: TaskService = Depends(get_task_service)):
    task = await service.get_by_id(task_id)
    if task is None:
        raise TaskNotFoundException(task_id)
    return TaskResponse.model_validate(task)
```

## Reference

- App factory / exception handler: `backend/application/src/main.py`
- Schemas: `backend/adapters/rest/src/schemas/`

## Verify

- `pytest backend/adapters/rest/tests/routers/test_{resource}_router.py` GREEN. File ≤ 200 lines.
