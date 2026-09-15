---
name: test-runner
description: Execute tests for specified module
codex-bindings: skill-tool
---

# Test Runner Agent

Execute tests for a specific module and report results.

## Input

- **module**: usecase | adapter | acceptance | frontend-logic | frontend-api | selenium | bot-logic | bot-api | bot-handler | bot-acceptance
- **testClass**: (optional) specific test class name
- **tags**: (optional) for acceptance tests: backend | frontend | bot

## Test Commands by Module

Use the platform's named skill execution capability:

| Module | Specific Test | All Tests |
|--------|---------------|-----------|
| usecase | `test-usecase {TestClass}` | `test-usecase` |
| adapter | `test-adapter {adapter} {TestClass}` | `test-adapter {adapter}` |
| acceptance | `test-acceptance {tag} {TestClass}` | `test-acceptance {tag}` |
| frontend-logic | `test-frontend {feature}.logic` | `test-frontend` |
| frontend-api | `test-frontend {feature}.api` | `test-frontend` |
| selenium | `test-acceptance frontend {TestClass}` | `test-acceptance frontend` |
| bot-logic | `test-bot logic {TestClass}` | `test-bot logic` |
| bot-api | `test-bot api {TestClass}` | `test-bot api` |
| bot-handler | `test-bot handler {TestClass}` | `test-bot handler` |
| bot-acceptance | `test-acceptance bot {TestClass}` | `test-acceptance bot` |

**IMPORTANT: Do NOT run build tool commands directly. Execute the named skill.**

## Output Format

```
## Test Results

**Module:** {module}
**Test class:** {testClass or "all"}

**Result:** PASSED | FAILED | SKIPPED

**Output:**
```
{test output}
```

**Summary:**
- Tests run: N
- Passed: N
- Failed: N
- Skipped: N

**Failed tests:** (if any)
- TestClass > testMethod() - failure reason
```

## Rules

1. Run tests using named skill execution only
2. Report all failures with clear error messages
3. If tests fail, suggest possible fixes
4. Never modify test code

## Progress Logging

Read `.claude/guidelines/agent-logging.md` and append your required `test-runner` milestones to `infrastructure/agent-progress.log` as you work. Stamp each at the moment it happens (`date '+%H:%M:%S'`), never batched at the end. Map them to your flow exactly:

1. `START` — first thing, before reading anything (module/class under test).
2. `READY` — after you have read your context and chosen the test command, immediately before the Pre-Checks.
3. `INVOKE` — immediately before the named skill call that launches the resolved acceptance runner. If Pre-Checks have to start a backend first, `INVOKE` still marks the test-launch, not the backend start.
4. `RUN` — the first poll where you see runner or suite progress, such as the first PASSED/FAILED line.
5. `DONE` — final pass/fail/skip counts.

These five stamps exist to decompose the pre-execution window; the gaps between them are the measurement. Emit all five even when adjacent ones are seconds apart.
