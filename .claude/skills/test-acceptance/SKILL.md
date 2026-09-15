---
name: test-acceptance
description: Run application-level E2E acceptance tests using the commands declared in ProductSpecification/technology.md. Use for backend API acceptance tests or for another application suite once that suite has been bootstrapped.
---

# Run Acceptance Tests

## Route the Request

Read `ProductSpecification/technology.md` before selecting a command.

| Input | Target | Scope |
|---|---|---|
| no argument | backend | all API acceptance tests |
| `backend` | backend | all API acceptance tests |
| `backend {filter}` | backend | API tests matching `{filter}` |
| `{filter}` | backend | API tests matching `{filter}` |
| `frontend`, `bot`, or `load` | named suite | all tests in that suite |
| `frontend {filter}`, `bot {filter}`, or `load {filter}` | named suite | matching tests in that suite |

Treat `backend`, `frontend`, `bot`, and `load` as reserved target names. Any
other first argument is a backend filter.

For an explicitly named non-backend target, read that application's
conventions. If its acceptance command is missing or marked unavailable, STOP
and report that the application has not been bootstrapped. Never borrow another
application's environment, port, run command, or test command.

## Backend Pre-Check

Read these values from the Backend conventions:

- Environment file
- Environment setup command
- Run command
- External host variable
- Port variable
- Health endpoint
- Acceptance test command
- Focused acceptance test command

Require the declared environment file. If it is absent, execute the declared
environment setup command and then re-read it.

Check the declared health endpoint using the host and port loaded from that
environment file. Never hardcode a host or port.

If the health check is unavailable or does not return HTTP 200:

1. Start the backend with the declared run command, using `/run-backend` when
   that skill provides the binding.
2. Keep the process pollable and retain its session identifier.
3. Wait for the declared health endpoint to return HTTP 200.
4. If startup fails, report the startup error and do not invoke the tests.

## Invoke the Suite

Use the exact command declared in the selected application's conventions.

- Full backend suite: run `Acceptance test command` unchanged.
- Focused backend suite: substitute the requested expression into
  `Focused acceptance test command` as one filter value.
- Do not pass the literal target name `backend` to the underlying test runner.

Run the suite as a persistent, pollable process. Do not use a blocking wrapper
that hides progress until completion.

## Execution Protocol

Read `.claude/guidelines/tdd-rules.md` before running the suite and follow its
first-failure protocol.

Poll output at intervals of no more than 30 seconds. For the Python API suite,
look for pytest progress and terminal signals such as collection errors,
`PASSED`, `FAILED`, `ERROR`, and the final passed/failed/error counts. Also
inspect process completion; do not infer success from one output line.

On the first failure:

1. Stop the test process if it is still running.
2. Preserve the failure output and any available counts.
3. Distinguish infrastructure/startup failure, collection failure, and an
   application assertion failure.
4. Report the failing test and the next concrete action.

## Report

Report:

- target application and whether the run was full or focused;
- command selected from the technology conventions;
- passed, failed, error, and skipped counts when pytest reports them;
- whether a backend process was started and left running;
- suites that were explicitly requested but unavailable.
