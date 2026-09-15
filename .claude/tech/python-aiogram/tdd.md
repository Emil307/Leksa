# Python/aiogram TDD Idioms

Tech binding for bot tests using pytest and pytest-asyncio.

## Test Layers

- Bot logic: pure tests under `bot/tests/logic/`.
- API client: HTTP contract tests under `bot/tests/api/` using a strict fake
  transport; no live API and no database.
- Handlers: direct async tests under `bot/tests/handlers/` with fake aiogram events,
  fake FSM context, and a recording fake API client.
- Bot E2E: dispatcher-driven tests under `bot/e2e/` with real handlers and
  middlewares, isolated FSM storage, a strict API stub, and a recording Telegram transport.

## Handler Tests

- Call the handler directly with the smallest event object exposing what it reads.
- Assert exact reply text/keyboard, FSM state, and API-client call arguments.
- Prefer recording fakes over broad `AsyncMock` assertions.
- Never use API repositories or direct database setup in bot tests.

## API Client Tests

- Match HTTP method, path, headers, and serialized body exactly.
- Return a representative API response and assert the fully parsed typed result.
- Cover API validation/authorization errors and transport unavailability separately.
- The fake transport must reject any unregistered request.

## E2E Tests

- Feed crafted `Update` objects through the real `Dispatcher`.
- Assert the outgoing Telegram operation and the exact HTTP interaction with the API stub.
- Reset FSM storage and transport recordings between scenarios.
- Cross-application tests against a real API belong to the Integration category, not the
  bot application's isolated E2E suite.

## RED and GREEN

- Disable marker: `@pytest.mark.skip(reason="RED: ...")` after verifying the predicted
  failure.
- Typical RED failures are a missing handler/client method, an unexpected HTTP request,
  a wrong FSM state, or a strict reply mismatch.
- GREEN changes production code only; tests are read-only except for removing the marker
  in the final E2E-green phase.
