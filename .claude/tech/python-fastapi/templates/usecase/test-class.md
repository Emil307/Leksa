# Service (Usecase) Test Template — python-fastapi

> Universal rules: `.claude/templates/tdd/red-usecase.md`

The usecase layer is `backend/usecase/src/services/`. One service = one user-visible operation orchestrator.

## 3-Tier Locations

| Tier | Location |
|------|----------|
| Test Class | `backend/usecase/tests/{feature}/test_{feature}_usecase.py` |
| Statements | `backend/usecase/tests/statements/{feature}_statements.py` |
| Scope | `backend/usecase/tests/scope/{feature}_request_scope.py` |
| Fakes | `backend/usecase/tests/fake/{feature}/fake_{feature}_repository.py` |

## Test Class Rules

- `class TestServiceName:` with `async def test_should_{behavior}` methods, `@pytest.mark.asyncio`.
- Class-level docstring describes the scenario in plain English.
- Inject a **fake repository** (in-memory, implementing the port `Protocol`) — never the real SQLAlchemy repo, never a bare `Mock` for the whole repo. Construct the service with the fake, or monkeypatch the `get_x_repository` factory.
- No assertions and no control flow in the test class — they belong in Statements (see `tdd.md`, 3-Tier Test Architecture).
- Never pre-seed a fake storage from Statements — set data up through the usecase that writes it.

## Fake Repository Pattern

```python
class FakeTaskRepository:
    def __init__(self):
        self._by_id: dict[UUID, Task] = {}
    async def get_by_id(self, task_id: UUID) -> Optional[Task]:
        return self._by_id.get(task_id)
    async def create(self, data: TaskCreate) -> Task:
        task = Task(**data.model_dump())
        self._by_id[task.id] = task
        return task
```

## Failure Patterns (RED)

| Current implementation | Expected test failure |
|------------------------|-----------------------|
| method missing / `raise NotImplementedError()` | `NotImplementedError` |
| `return None` | `assert result == expected` |
| stubbed wrong value | `assert result.field == expected` |
| domain rule not enforced | `pytest.raises(SomeDomainException)` does not raise |

## Reference (read before generating)

- Service example: `backend/usecase/src/services/user.py`
- Entity + Create/Update models: `backend/domain/src/entities/user.py`
- Port `Protocol` to fake: `backend/usecase/src/ports/user_repository.py`
- Statements example: `backend/usecase/tests/statements/user_statements.py`
- Scope example: `backend/usecase/tests/scope/user_request_scope.py`
- TestData: `backend/usecase/tests/scope/test_data.py`
- Fixtures: `backend/usecase/tests/conftest.py`

## Update conftest.py

Register the new service, its fake repository, and the new Statements as fixtures in
`backend/usecase/tests/conftest.py`, following the existing sections. A Statements class that is
not wired into a fixture cannot be injected into the test class.

## Naming

- Test file: `backend/usecase/tests/{feature}/test_{feature}_usecase.py`
- Test method: `test_should_{expected_behavior}`
- Statements: `{Feature}Statements`, Scope: `{Feature}Scope`
