# Bot E2E Test Template — python-aiogram

## Location

`bot/e2e/test_{feature}_flow.py`

## Rules

- Build the real `Dispatcher` with production handlers and middlewares.
- Use isolated FSM storage, a strict API HTTP stub, and a recording Telegram transport.
- Feed crafted `Update` objects through `Dispatcher.feed_update`.
- Keep the test declarative through Statements/helpers that build updates and assert
  outgoing operations.
- Assert both observable Telegram output and the exact API request.
- Never assert database rows directly; API-owned state is observable only through its
  HTTP contract.

## Failure Patterns

| Current state | Expected failure |
|---|---|
| handler not wired | no recorded Telegram operation |
| wrong API request | strict HTTP stub rejects request |
| wrong conversation state | next update produces wrong response/state |
| error mapping absent | raw error or wrong user-visible reply |
