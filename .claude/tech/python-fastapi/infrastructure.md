# Python/FastAPI Infrastructure Idioms

Tech binding for `infrastructure.md`. Load alongside the universal rules.
Run/test/coverage commands are **not** duplicated here — they live in the `technology.md`
Conventions table (values to copy in are listed at the bottom of this file).

## Ports & Config

- All ports/credentials flow through `infrastructure/.env` (loaded by `pydantic-settings`). NEVER hardcode a port — read from settings (`settings.app.port`, `settings.db.port`) or `.env`.
- Compose reads the same `.env` (`${VAR}` / `${VAR:-fallback}`).

## Health Check

- `source infrastructure/.env && curl http://localhost:$BACKEND_PORT/health` — add a `/health` route in the app factory if absent.

## Database & Migrations

- Engine: `create_async_engine(settings.db.url)` with `pool_pre_ping=True`. Sessions via a `get_session()` async generator; transactions via `UnitOfWork`.
- Migrations (Alembic): create `alembic revision --autogenerate -m "..."`, apply `alembic upgrade head`. Versions live under `backend/adapters/storage/src/migrations/versions/`.
- NEVER edit the running DB by hand — change the ORM model and generate a migration.

## Process Safety

- Never kill by name (`pkill python` / `killall python`) — that kills parallel sessions. Stop only the container/PID you started, via the repo's port-based stop script.
- Never remove containers you did not start; manage only this repo's compose project.

## Config Fallback Syntax

- Python: `pydantic-settings` `Field(default=..., env="VAR")` / `os.environ.get('VAR', 'fallback')`.
- Docker Compose / shell: `${VAR:-fallback}` (colon-dash).

## Acceptance Tests

- Acceptance tests are black-box: they run against the **started stack** (`run-infra.sh` → `migrate.sh` → `run-backend.sh`) over HTTP, with the base URL derived from `BACKEND_PORT` in `.env`. Never in-process via `ASGITransport`, never importing the app — that is the REST *adapter* test pattern, not acceptance.
- `test-acceptance.sh` exports the env vars, waits for `/health`, then runs `pytest acceptance/`.

## Conventions Values (copy into `technology.md`)

| Concern | Value |
|---------|-------|
| Test disable marker | `@pytest.mark.skip(reason="RED: ...")` |
| Not-implemented marker | `raise NotImplementedError()` |
| Run command | `uvicorn application.main:app --host $BACKEND_HOST --port $BACKEND_PORT` |
| Test command | `pytest backend/{module}` |
| Acceptance test command | `pytest acceptance/` |
| Coverage report | `coverage.xml` (`pytest --cov=backend --cov-report=xml`) |
| Health endpoint | `/health` |
| Config syntax | `os.environ.get('VAR', 'fallback')` / `${VAR:-fallback}` |
