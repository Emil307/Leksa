# Acceptance Test Implementation (Green Phase) — python-fastapi

> Universal workflow: `.claude/templates/tdd/green-acceptance.md`

The only change is removing the disable marker from ONE test. No production code, no new
handlers, no wiring — if the test needs code that does not exist, a `red-adapter` /
`green-adapter` prerequisite step was missed.

## Tech-Specific Details

- **Disable marker**: `@pytest.mark.skip(reason="TDD Red Phase - Not yet implemented")` — remove to
  enable, re-add on failure
- **Test target**: `acceptance/tests/backend/{feature}/test_{feature}_acceptance.py::{TestClass}`
  (the filter passed to `test-acceptance`)
- **Error terminology**: "exception handlers" (`@app.exception_handler` registered by the app factory)

## Prerequisites

- The stack is running from `infrastructure/` (`run-infra.sh` → `migrate.sh` → `run-backend.sh`);
  `alembic upgrade head` has been applied before the suite starts.
- Ports/base URL come from `infrastructure/.env` — the acceptance module never starts the app
  in-process and never opens a DB session.

## Collateral Failures

Shared state across scenarios is the common cause. Acceptance tests isolate through **the API**
(unique test data per scenario via `TestData`), never by truncating tables or rolling back a
session from the test — the suite has no DB access.
