# Telegram Handler Test Template — python-aiogram

## Location

`bot/tests/handlers/test_{feature}_handlers.py`

## Rules

- Use `@pytest.mark.asyncio` and call the handler directly.
- Supply a fake `Message`/`CallbackQuery`, fake `FSMContext`, and recording fake API client.
- Assert exact reply content, FSM state/data, and API-client call arguments.
- The fake API client returns typed response objects or raises typed client errors.
- Never import API application modules, use API repositories, or prepare database state.

## Failure Patterns

| Current state | Expected failure |
|---|---|
| handler missing | import or attribute error |
| API call absent/wrong | strict recording mismatch |
| reply absent/wrong | exact answer assertion fails |
| FSM transition wrong | exact state/data assertion fails |

## Test Support

- Fake event objects expose only attributes the handler reads and record `answer()` calls.
- Fake FSM context is dictionary-backed and reset per test.
- Recording API client rejects unexpected calls and records exact arguments.
