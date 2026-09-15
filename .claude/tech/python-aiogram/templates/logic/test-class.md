# Bot Logic Test Template — python-aiogram

## Location

`bot/tests/logic/test_{feature}_logic.py`

## Rules

- Test pure bot presentation or conversation decisions without dispatcher, network,
  FSM storage, or API application imports.
- Pass typed values and errors as inputs; assert the complete returned view/state value.
- Cover each branch and boundary value with exact equality.
- Keep expected user-visible text in the test or shared test data, never in a fake.

## Failure Patterns

| Current state | Expected failure |
|---|---|
| function missing | import or attribute error |
| branch absent | exact result mismatch |
| error mapping absent | raw error or wrong view state |
| boundary mishandled | strict equality failure |
