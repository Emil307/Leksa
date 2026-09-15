# Storage (Repository) Test Template — python-fastapi

The storage adapter is `backend/adapters/storage/src/` (SQLAlchemy async + `SQLAlchemyRepository` + `UnitOfWork`).

## Test Class Rules

- `class TestXRepository:` with `@pytest.mark.asyncio` `async def test_should_{behavior}` methods.
- Run against a real Postgres test schema (or async SQLite fallback) via a `pytest-asyncio` async fixture that creates the engine/session and rolls back / truncates per test.
- Class-level docstring with a Gherkin-style description.
- Assert on **domain entities** returned by the mapper, not on `XModel` rows.
- Reproduce the real usecase flow: write through the port the writing usecase uses, read through the port the reading usecase uses (write-here-read-there), not a same-port save→read round-trip.

## Storage-Specific Failure Patterns (RED)

| Current implementation | Expected test failure |
|------------------------|-----------------------|
| `raise NotImplementedError()` | `NotImplementedError` |
| `return None` | `assert result == expected` |
| `return []` | `assert result == expected` |
| missing column / mapper field | `AttributeError` or field mismatch on the returned entity |

## Reference (read before generating)

- Repository example: `backend/adapters/storage/src/repositories/user.py`
- Repository base (get_one/add_one/update_one): `backend/adapters/storage/src/repositories/_base.py`
- ORM model example: `backend/adapters/storage/src/models/user.py`
- Mapper example: `backend/adapters/storage/src/mappers/user.py`
- Session/engine: `backend/adapters/storage/src/database.py`
- Port `Protocol` the repository implements: `backend/usecase/src/ports/`

## Naming

- Test file: `backend/adapters/storage/tests/repositories/test_{entity}_repository.py`
- Test method: `test_should_{expected_behavior}`
