# Leksa

Product monorepo for the Leksa API, frontend, and bot. Each application is
independently built and deployed, while product stories, tasks, and technology
decisions live in the shared `ProductSpecification/` directory.

The development framework works with both Claude Code and Codex. Canonical
process rules live in `CLAUDE.md` and `.claude/`; `AGENTS.md`, `.agents/`, and
`.codex/` provide the Codex bindings.

In Claude Code, invoke framework skills as `/skill-name`. In Codex, use
`$skill-name` (for example, `$continue`). Codex custom-agent adapters are
generated from the canonical `.claude/agents/*.md` files. Validate the complete
compatibility layer with:

```bash
.venv/bin/python .codex/scripts/check_codex_compat.py
```

When agent definitions change, regenerate the thin adapters with
`.venv/bin/python .codex/scripts/sync_claude_agents.py`.

## Repository layout

```
ProductSpecification  shared product specifications and work tracking
backend               FastAPI backend modules
acceptance            black-box API acceptance tests
infrastructure        API infrastructure and operational scripts
frontend              independently deployed frontend application
bot                   independently deployed bot application
```

`frontend/` and `bot/` are placeholders until their applications are imported.

## API

The API uses a Clean Architecture multi-module layout:

```
backend/domain            entities, value objects, business rules
backend/usecase           thin orchestrators + ports              -> domain
backend/adapters/rest     FastAPI routers and schemas              -> usecase
backend/adapters/storage  SQLAlchemy repositories and migrations   -> usecase
backend/adapters/email    SMTP sender                              -> usecase
backend/application       app factory and wiring                   -> all modules
acceptance                black-box HTTP tests
infrastructure            compose file, environment, and scripts
```

Dependency flow is inward only. It is declared in each backend module's
`pyproject.toml` and enforced by `lint-imports` using `.importlinter`.

## Setup

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
```

Each backend module installs editable, so `import domain`, `import usecase`,
`import adapter_storage`, … resolve from anywhere in the repo.

## Running

```bash
infrastructure/scripts/setup-ports.sh
infrastructure/scripts/run-infra.sh
infrastructure/scripts/migrate.sh
```

```bash
infrastructure/scripts/run-backend.sh
```

API ports come from `infrastructure/.env`, which is generated and ignored by Git.

## Tests

```bash
.venv/bin/python -m pytest backend
```

```bash
infrastructure/scripts/test-acceptance.sh
```

```bash
.venv/bin/lint-imports
```

Coverage from the repository root:

```bash
.venv/bin/python -m pytest backend --cov=backend --cov-report=xml:coverage.xml
```

## Migrations

```bash
infrastructure/scripts/migrate.sh revision --autogenerate -m "add words"
```

Then review the generated file under
`backend/adapters/storage/src/adapter_storage/migrations/versions/` and apply it
with `infrastructure/scripts/migrate.sh` from the repository root.
