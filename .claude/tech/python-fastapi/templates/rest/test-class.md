# REST (FastAPI router) Test Template — python-fastapi

> Universal rules: `.claude/templates/tdd/red-rest.md`

Covers HTTP endpoints in `backend/adapters/rest/src/routers/`.

## Test Class Rules

- `@pytest.mark.asyncio` `async def test_should_{behavior}` in `class TestXRouter:`.
- Drive the ASGI app in-process: `httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://test")`.
- Stub the service with a fake (constructor injection or `app.dependency_overrides`), never hit the real DB.
- Assert on **status code AND parsed body fields** (`resp.status_code == 200`, `resp.json()["id"] == ...`).
- One test class per router endpoint; the class may hold several methods (happy path, error, edge) — use a class-level disable marker in RED.

## Failure Patterns (RED)

| Current implementation | Expected test failure |
|------------------------|-----------------------|
| route missing | `assert resp.status_code == 200` fails with 404 |
| `return {}` stub | `assert resp.json()["field"] == expected` |
| wrong status mapping | `assert resp.status_code == 201` fails with 200 |

## Reference (read before generating)

- App factory + exception handler: `backend/application/src/main.py`
- Router example: `backend/adapters/rest/src/routers/user.py`
- Request/response schemas: `backend/adapters/rest/src/schemas/`

## Naming

- Test file: `backend/adapters/rest/tests/routers/test_{resource}_router.py`
- Test method: `test_should_{expected_behavior}`
