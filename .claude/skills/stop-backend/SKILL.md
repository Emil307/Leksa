---
name: stop-backend
description: Stop the running backend application. Use when user wants to stop the backend server or mentions /stop-backend command.
---

# Stop Backend Application

## Action

Stop the persistent backend process through the platform's process-control
capability, using the process/session ID returned by `/run-backend` (Claude) or
`$run-backend` (Codex).

If task ID unknown, use the stop script (reads port from `.env`):
```bash
infrastructure/scripts/stop-backend.sh
```

## Output

Report: backend stopped.
