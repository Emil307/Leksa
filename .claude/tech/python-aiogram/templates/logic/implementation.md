# Bot Logic Implementation Template — python-aiogram

## Rules

- Implement pure bot-only presentation and conversation decisions under
  `bot/src/bot_app/logic/`.
- Keep transport, dispatcher, FSM storage, and API calls outside this layer.
- Accept and return typed values; map typed API-client errors to bot view states here
  only when the mapping is presentation logic.
- Implement only branches required by the enabled focused test.

## Verify

- Run the focused bot logic test command from `technology.md` with `bot` as cwd.
- Run the complete bot unit-test command before returning.
