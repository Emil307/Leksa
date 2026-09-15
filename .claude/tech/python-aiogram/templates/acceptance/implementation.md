# Bot E2E Implementation Template — python-aiogram

## Rules

- Wire the real dispatcher, handlers, middlewares, bot-local logic, and typed HTTP client.
- Replace only external boundaries: isolated FSM storage, strict API HTTP stub, and
  recording Telegram transport.
- Never connect to the API database or import API application code.
- Implement only the slice required by the scenario; no speculative handlers.

## Checklist

- Handler/router registration matches the crafted update.
- Middleware supplies bot-local dependencies.
- API client sends the expected method, path, headers, and body.
- Reply and keyboard match exactly.
- FSM and recordings reset between scenarios.

## Verify

- Run the focused Bot E2E command from `technology.md` with `bot` as cwd.
