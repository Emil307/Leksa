# Acceptance Test Template — python-fastapi

> Universal structure and rules: `.claude/templates/tdd/red-acceptance.md`

Black-box tests over the **running** application, driven over HTTP with `httpx` and over the
browser via the `browser-testing` profile. The `acceptance/` module has no compile dependency on
backend internals — it never imports the ASGI `app`, the ORM models, or the storage session.

## Framework Rules

- Inherits from `AbstractBackendTest` (backend) or `AbstractUiTest` (frontend)
- `@pytest.mark.skip(reason="TDD Red Phase - Not yet implemented")` on the test class
- Not-implemented marker: `raise NotImplementedError()` — for real adapters only; Statements stay
  fully functional in RED
- `@pytest.mark.asyncio` on `async def test_should_{behavior}`; class-level docstring carries the
  Gherkin scenario
- Statements are plain classes instantiated in `conftest.py` fixtures
- Base URL comes from `infrastructure/.env` (`BACKEND_PORT`) — never hardcoded, never in-process

## Test Types

| Type | Base Class | Marker |
|------|------------|--------|
| Backend API | `AbstractBackendTest` | `@pytest.mark.backend` |
| Frontend UI | `AbstractUiTest` | `@pytest.mark.frontend` |

## 3-Tier Locations

| Tier | Location | Owns |
|------|----------|------|
| Test Class | `tests/backend/{feature}/` or `tests/frontend/{feature}/` | Gherkin scenario, flat sequence of Statements calls |
| Statements | `statements/` | Setup sequences and assertions; calls the client |
| Client | `clients/application/` | `httpx.AsyncClient`, base URL resolution, request building, response parsing |
| DTOs | `clients/application/dto/{feature}/` | Request/response dataclasses returned by the client |

**`httpx` is imported by the client tier only.** Statements never import an HTTP library, never
build URLs, never read `resp.status_code` — they call `await self.task_client.create(...)` and
assert on the returned DTO (`tdd-rules.md`, Acceptance Test Client Layer; test-review item 26).

## Failure Patterns (RED)

| Current state | Expected failure |
|---------------|------------------|
| feature not wired end-to-end | 404 / 500 surfaced by the client as a raised error |
| stub returns placeholder | `assert actual.field == expected` in Statements |
| endpoint returns no body | DTO parsing fails on the missing field |

## Reference (read before generating)

- Test example: `acceptance/tests/backend/{feature}/test_{feature}_acceptance.py`
- Base classes: `acceptance/tests/backend/abstract_backend_test.py`, `acceptance/tests/frontend/abstract_ui_test.py`
- Statements example: `acceptance/statements/{feature}_statements.py`
- Client: `acceptance/clients/application/application_client.py`
- DTOs: `acceptance/clients/application/dto/`
- TestData: `acceptance/statements/test_data.py`
- Fixtures: `acceptance/conftest.py`

## Naming

- Test file: `acceptance/tests/backend/{feature}/test_{feature}_acceptance.py`
- Test method: `test_should_{expected_behavior}`
- Statements: `{Feature}Statements`, Client: `{Feature}Client`

## Key Paths

- Backend tests: `acceptance/tests/backend/`
- Frontend tests: `acceptance/tests/frontend/`
- Statements: `acceptance/statements/`
- Client: `acceptance/clients/application/`
- DTOs: `acceptance/clients/application/dto/`
