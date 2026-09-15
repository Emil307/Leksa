# Python/aiogram Coding Idioms

Tech binding for a standalone bot application built with Python and aiogram 3.x.
The bot is an independent API client: it never imports the API application's domain,
usecases, adapters, or persistence code.

## Application Structure

- `bot/src/bot_app/handlers/`: message and callback handlers.
- `bot/src/bot_app/logic/`: bot-only presentation and conversation logic.
- `bot/src/bot_app/api/`: typed HTTP client, request/response models, error mapping.
- `bot/src/bot_app/middlewares/`: aiogram `BaseMiddleware` implementations.
- `bot/src/bot_app/config/`: FSM states, typed callback data, commands, keyboards.
- `bot/src/bot_app/application.py`: bot, dispatcher, middleware, and transport wiring.

## Dependency Boundary

- Handlers may call bot-local logic and the typed API client interface.
- The API client communicates with the product API exclusively over HTTP using
  `API_BASE_URL` from the bot's own environment.
- Never import from `backend/` or copy API domain entities into the bot.
- Never connect the bot to the API database or invoke API repositories/usecases directly.
- Server-owned validation, authorization, and business rules stay in the API. Bot-side
  checks are UX only and the API response remains authoritative.

## Handlers

- A handler parses one update, calls one bot operation or API-client method, and renders
  one observable response. Handlers never call other handlers.
- Rendering goes through keyboard builders and reply helpers rather than scattered inline
  text/keyboard construction.
- Translate typed API errors into user-facing bot states at one boundary; do not expose
  raw transport errors or response bodies.

## FSM and Callback Data

- Multi-step flows use `StatesGroup` and `FSMContext`.
- Production FSM storage is external and shared across instances; never use module-level
  dictionaries or `MemoryStorage` in production.
- Use typed `CallbackData`; never parse raw callback strings by hand.
- Store only conversation state in FSM. API-owned entities and authorization state are
  fetched from the API when needed.

## Naming

- Handler module: `handlers/{feature}.py`; handler: `process_{action}_{command|callback}`.
- API client module: `api/{resource}.py`; client class: `{Resource}ApiClient`.
- Callback class: `{Feature}Callback`; state group: `{Feature}State`.
