---
name: test-all
description: Run every bootstrapped application's unit tests in parallel, then its acceptance suites. Use when the user wants the full repository test suite or mentions /test-all.
---

# Run All Tests

Runs the complete test suite: unit tests in parallel, then acceptance tests.

## Setup

Read `ProductSpecification/technology.md` Conventions table for:
- **Backend test command** pattern (with module substitution)
- **Frontend test command**
- **Bot test command**
- **Acceptance test command**

A command marked unavailable means that application is still a placeholder. Do not
invent a command; report its suites as unavailable and exclude them from the active
repository suite.

Discover backend adapter modules by listing directories under `backend/adapters/`.

## Workflow

### Phase 1: Run Unit Tests in Parallel

Run ALL of these commands concurrently using multiple shell calls started before
awaiting any result:
- Backend usecase tests: `{Backend test command}` with module = usecase
- Backend adapter tests: one `{Backend test command}` per adapter module discovered
- Frontend tests: `{Frontend test command}`
- Bot tests: execute `/test-bot` when the Bot test command is available

Wait for all to complete. If any fail, report failures and STOP.

### Phase 2: Start Backend

Execute the named `run-backend` skill and await startup.

Wait for backend to start.

### Phase 3: Run Acceptance Tests

```
{Acceptance test command} for backend tests
```

Run `test-acceptance frontend` and `test-acceptance bot` when their application
conventions declare available acceptance commands.

### Phase 4: Stop Backend

Execute the named `stop-backend` skill and await completion.

## Output

Report summary:
- Backend unit tests: PASS/FAIL (usecase + each adapter)
- Frontend unit tests: PASS/FAIL/UNAVAILABLE
- Bot unit tests: PASS/FAIL/UNAVAILABLE
- Acceptance tests per application: PASS/FAIL/UNAVAILABLE (with details if failed)
- Overall: PASS/FAIL
