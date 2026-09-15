---
name: test-bot
description: Run bot logic, API-client, and handler tests using commands declared in ProductSpecification/technology.md. Use for bot unit tests or a focused bot implementation lane.
---

# Run Bot Tests

## Route the Request

Read the Bot conventions in `ProductSpecification/technology.md`.

| Input | Convention |
|---|---|
| no argument or `all` | Test command |
| `logic` | Logic test command |
| `logic {filter}` | Focused logic test command |
| `api` | API-client test command |
| `api {filter}` | Focused API-client test command |
| `handler` | Handler test command |
| `handler {filter}` | Focused handler test command |

Treat the optional filter as one test-runner value. Execute the command with the
declared Bot root as the working directory.

If the selected command is absent or marked unavailable, STOP and report that the
bot has not been bootstrapped. Never substitute the backend Python environment,
test command, or API port variables.

Run the selected command as a persistent, pollable process. Follow
`.claude/guidelines/tdd-rules.md` for first-failure handling and report passed,
failed, error, and skipped counts.
