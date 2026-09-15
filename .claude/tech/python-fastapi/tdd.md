# Python/FastAPI TDD Idioms

Tech binding for `tdd-rules.md`. Load alongside the universal rules.
Test runner: **pytest + pytest-asyncio**. Add `pytest`, `pytest-asyncio`, `pytest-cov` to `requirements.txt`.

## Test Disable Marker

- `@pytest.mark.skip(reason="RED: <predicted failure>")` on the test function/class.
- RED: add the marker AFTER validating the predicted failure. GREEN: removing the marker is the ONLY allowed test edit.
- RED commits include the skipped test.

## Async Tests

- `@pytest.mark.asyncio` on `async def test_...` (or `asyncio_mode = auto` in `pytest.ini`).
- Await the service/repository directly: `result = await service.create_task(...)`.

## Test Description

- `class TestFeatureName:` with methods `test_should_{expected_behavior}`. Class/module docstring states the scenario in plain English.

## Stub Pattern

- Real adapters (repositories, HTTP clients) stub with `raise NotImplementedError()` in RED.
- Fakes are functional, not stubbed — see Test Data below.

## Domain Stub Examples

- Give a new entity only the fields the test asserts. When a constructor/`XCreate` gains a field, patch callers with sensible defaults (enum `.value`, `None`).
- Never widen a Pydantic model with fields no test needs yet.

## Build Green in RED — Forbidden Changes

- No new SQLAlchemy `XModel` columns, no `mapped_column` additions, no Alembic revisions during RED — those are GREEN implementation.
- No mapper `build_*_dict` changes during RED.

## GREEN Phase Artifacts

- Production code, SQLAlchemy models/columns, mappers, repositories, Alembic migrations (`alembic revision --autogenerate` / `alembic upgrade head`).

## 3-Tier Test Architecture — Python Specifics

### Test Class
- See the universal 3-Tier rules in `tdd-rules.md` (no assertions, no control flow, no private members in the test class).
- Python markers of a violation: `assert` / `pytest.raises` in the test class, `for`/`while`/`if`, functions named `_helper` (leading underscore), nested `class` definitions inside the test class.
- `async def test_...` still delegates: `await task_statements.create_task(login)` — the `await` lives in the test class, the HTTP/repository call lives in Statements.

### Statements
- Plain classes (not `unittest.TestCase`) with `async def` methods; instantiated by a `pytest` fixture that receives the fakes/clients.
- Statements are fully functional in RED — never `raise NotImplementedError()` in a Statements method.
- **Acceptance Statements never import `httpx`.** The client tier (`acceptance/clients/application/`)
  owns `AsyncClient`, base URL resolution, request building, and response parsing; Statements call
  the client and assert on the returned DTO (`tdd-rules.md`, Acceptance Test Client Layer).

### Scope
- `@dataclass(frozen=True)` with a `@classmethod` builder accepting `**overrides`, or a Pydantic model with `model_copy(update=...)`.
- Implementation: `DEFAULTS` dict + `@classmethod def builder(cls, **overrides) -> Scope` merging `{**cls.DEFAULTS, **overrides}`.
- Example: `scope = TaskScope.builder(email="test@example.com")` — all defaults except `email`.
- `frozen=True` keeps scopes immutable value objects.

## Test Data & Isolation

- **Usecase (service) tests**: inject a **fake repository** — a plain class implementing the same port `Protocol` over an in-memory `dict`/`list`. No DB, no mocks-of-mocks. Override the factory via monkeypatch or constructor injection.
- **Storage adapter tests**: run against a real Postgres test schema (or an async SQLite fallback). Wrap each test in a transaction rolled back in teardown, or truncate tables in a fixture. Use `pytest-asyncio` async fixtures for engine/session.
- **REST adapter tests**: `httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://test")`. Stub the service with a fake via `app.dependency_overrides`.
- Mocks: `unittest.mock.AsyncMock` for async collaborators; `reset_mock()` per test via fixture.

## Assertion Library (plain pytest)

- Strict equality: `assert actual == expected` (Pydantic/dataclass `==` is deep structural).
- Non-null (last resort only): `assert actual is not None`.
- Exceptions: `with pytest.raises(ValidationException):` — assert on `exc.value.code` too.
- Timestamp bounds: `assert actual > now - timedelta(seconds=30)`.
- Unordered collections: `assert set(actual) == set(expected)`; ordered: `assert actual == expected`.
- Reserve per-field assertions for custom comparators / field exclusions.

## Async Wait Pattern

- Waiting for a side effect: `tenacity` assertion-polling, never bare `asyncio.sleep`:
  ```python
  from tenacity import retry, stop_after_delay, wait_fixed
  @retry(stop=stop_after_delay(5), wait=wait_fixed(0.1))
  async def assert_eventually():
      assert await actual_value() == expected
  ```
- Negative ("nothing happened"): poll for a fixed duration asserting the condition holds throughout.

## Coverage Tool

- `pytest --cov=backend --cov-report=xml:coverage.xml --cov-report=term-missing`.
- Domain/usecase files checked against usecase-test coverage; storage files against storage-test coverage.
- Scan touched files across `backend/domain`, `backend/usecase`, `backend/adapters`.

## Test Filter Flag

- `pytest -k "ClassName"` or `pytest path/test_file.py::TestClass::test_method`.
- Acceptance: poll the output file for `PASSED|FAILED|ERROR` markers.

## Test Clock

- Inject a `Clock` protocol; use a `FakeClock` with `advance(seconds)` in tests instead of real time.

## Test Review Grep Patterns

| # | Check | Grep pattern |
|---|-------|-------------|
| 2 | Loose string assertions | `in actual\|is not None\|!= None\|assert len` |
| 3 | Range/direction checks | `assert .*[<>]` — scoped to assertions; a bare `> \|<` matches every comparison in production code |
| 4 | Loose mock matchers | `call_args\|ANY\|mock.ANY` |
| 6 | Partial collection coverage | `\[0\]` |
| 12 | Assertions in test class | `assert \|pytest.raises` |
| 21 | Calculated expected values | `math\.\|ceil\|floor\|% \|// \|len(.*) [*/]\|timedelta(.*[*/]` |
| 23 | Private functions in test class | `def _` |
| 26 | HTTP client in acceptance Statements | `httpx\.\|requests\.\|client.get\|client.post` |
