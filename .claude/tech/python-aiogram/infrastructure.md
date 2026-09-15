# Python/aiogram Infrastructure Idioms

Tech binding for the independently deployed bot application. Load alongside the
universal infrastructure rules.

## Independent Configuration

- Bot configuration comes from `bot/infrastructure/.env` or deployment-injected
  environment variables. It never reads the API application's `.env`.
- Required integration settings include `BOT_TOKEN` and `API_BASE_URL`.
- FSM settings belong to the bot (`REDIS_URL` or equivalent); database credentials do not.
- Missing required settings fail startup with the exact variable name.

## API Connectivity

- `API_BASE_URL` is an explicit URL supplied by the environment, not assembled from the
  API application's port variables.
- Apply finite connect/read timeouts and map transport failures to a stable unavailable
  state. Never retry non-idempotent API operations implicitly.
- The bot readiness check must distinguish dispatcher startup, FSM-storage availability,
  and API reachability when the deployment requires all three.

## Telegram Delivery

- Webhook and polling are deployment choices declared in `technology.md`; application
  behavior must not depend on which transport delivers an update.
- Webhook mode uses the bot's own HTTP entrypoint and public URL. It does not reuse the
  API application's FastAPI process.
- Register/remove the webhook during bot startup/shutdown, scoped to the bot deployment.

## Process Safety

- Run and stop commands come from the Bot conventions in `technology.md` and execute with
  `bot` as their working directory.
- Never kill Python processes by executable name. Stop only the PID or container belonging
  to this bot workspace instance.
