# Scheduling Adapter Test Template — python-fastapi

## Test Class Rules

- `class TestXJob:` with `@pytest.mark.asyncio` `async def test_should_{behavior}` methods.
- Scheduler under test is `APScheduler` (`AsyncIOScheduler`); override the schedule to fire every second so the test is fast.
- Mock the usecase with `AsyncMock` — scheduling tests verify **wiring**, not business logic.
- Poll for the async invocation with `tenacity`, never `asyncio.sleep`.
- Class-level docstring with a Gherkin-style description.

## Scheduling-Specific Failure Patterns (RED)

| Current implementation | Expected test failure |
|------------------------|-----------------------|
| job not registered | polling times out — `assert_awaited` never satisfied |
| wrong cron expression | job does not fire inside the window |
| missing distributed lock | lock row/key not found error |
| usecase called with wrong request | `assert_awaited_once_with(...)` argument mismatch |

## Reference (read before generating)

- Scheduler setup: `backend/adapters/scheduling/src/scheduler.py`
- Existing job: `backend/adapters/scheduling/src/jobs/cleanup_job.py`
- Config: `backend/adapters/scheduling/src/config.py`
- Test fixtures (fast schedule, lock table): `backend/adapters/scheduling/tests/conftest.py`

## Naming

- Test file: `backend/adapters/scheduling/tests/jobs/test_{job}.py`
- Test method: `test_should_{expected_behavior}`
