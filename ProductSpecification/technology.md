# Technology Profile

tech-profile:
  backend: java-spring
  frontend: react-ts
  css: tailwind
  browser-testing: selenium
  bot: python-aiogram

## Scope

This repository is a product monorepo. The API keeps the framework's legacy root layout:
`backend/`, `acceptance/`, and `infrastructure/`. Frontend and bot are independent
applications under `frontend/` and `bot/`; their deployment configuration and
infrastructure stay inside their own directories.

The API is active. The frontend is bootstrapped: a Vite + React + TypeScript application
under `frontend/` with its own scripts, Vitest/MSW unit lanes, and a standalone Selenium
Gradle project under `frontend/e2e/`. The bot is an existing pre-framework application being
adopted in place. It has its own source layout, webhook process, PostgreSQL database,
Redis storage, and migrations. Until the API/bot responsibility split is decided, the
bot's current database-backed behavior is preserved and its test lanes remain unavailable.

Frontend and bot never import backend production code or read API-local configuration.
The target bot boundary is HTTP-only communication with the API, but `API_BASE_URL` and
the typed API client are intentionally deferred until ownership is divided and redundant
bot behavior is removed.

## Backend

| Concern | Technology |
|---------|-----------|
| Language | Java 21 |
| Framework | Spring Boot 3 Web MVC (blocking, virtual threads) |
| Build tool | Gradle (Kotlin DSL), multi-module |
| DI | Spring constructor injection |
| Web | `@RestController` + records as request/response DTOs |
| Persistence | Spring Data JPA + Hibernate 6 + HikariCP |
| Database | PostgreSQL |
| Migrations | Liquibase (`backend/adapters/storage/src/main/resources/db/changelog/`) |
| Mail | Spring Mail (SMTP), MailHog in dev |
| Cache | Lettuce (Redis), Lua scripts |
| Config | `@ConfigurationProperties` records + `application.yml` |
| Code generation | Lombok (domain only), Java records |

## Testing (Backend)

| Concern | Technology |
|---------|-----------|
| Unit/integration | JUnit 5 |
| Assertions | AssertJ |
| Mocking | Mockito, in-memory fakes |
| Coverage | JaCoCo |
| Database (tests) | Testcontainers (`postgres:17-alpine`) |
| Mail (tests) | GreenMail |
| HTTP (adapter tests) | MockMvc |
| HTTP (acceptance) | `httpx` — the acceptance suite stays Python |
| Architecture check | ArchUnit (`backend/architecture`) |

## Infrastructure

| Concern | Technology |
|---------|-----------|
| Containerization | Docker / docker-compose |
| Mail server (dev) | MailHog |
| Application server | embedded Tomcat (Spring Boot) |

## Module Layout

Each backend module is a Gradle subproject with the standard Maven source layout and a
single root package:

| Module | Gradle project | Root package |
|--------|----------------|--------------|
| `backend/domain` | `:backend:domain` | `com.uwords.domain` |
| `backend/usecase` | `:backend:usecase` | `com.uwords.usecase` |
| `backend/adapters/rest` | `:backend:adapters:rest` | `com.uwords.adapter.rest` |
| `backend/adapters/storage` | `:backend:adapters:storage` | `com.uwords.adapter.storage` |
| `backend/adapters/email` | `:backend:adapters:email` | `com.uwords.adapter.email` |
| `backend/adapters/cache` | `:backend:adapters:cache` | `com.uwords.adapter.cache` |
| `backend/application` | `:backend:application` | `com.uwords.application` |
| `backend/architecture` | `:backend:architecture` | `com.uwords.architecture` |

Where a `.claude/tech/java-spring/` template writes a path like
`backend/usecase/src/main/java/{package}/service/{Name}.java`, the concrete package in
this repo is `com.uwords.usecase.service`.

**Controller wiring.** A controller must not import another adapter; it receives its
usecase service through the constructor and Spring supplies it. Composition lives in
`backend/application`, never in an adapter.

**Test support packages.** Per-module test helpers (Statements, Fakes) live under that
module's `src/test/java/{package}/testing/`. Acceptance keeps the framework layout:
`acceptance/{tests,statements,clients}/` and stays Python over HTTP.

Inward dependency flow is enforced by Gradle project dependencies and by
`LayerDependencyRulesTest` in `backend/architecture`. Run
`./gradlew :backend:architecture:test` to verify.

## Testing Layers

| Layer | Who tests it | Where |
|-------|--------------|-------|
| `domain` | **nobody, directly** — covered through usecase tests | — |
| `usecase` | one test class per scenario, port fakes, Statements | `backend/usecase/src/test/java/` |
| `adapters/*` | that adapter's own tests | `backend/adapters/{name}/src/test/java/` |
| `application` | wiring and configuration binding only | `backend/application/src/test/java/` |
| end-to-end | black-box over HTTP | `acceptance/` |

**`backend/domain/` has no test source set and must not grow one.** Business rules live
in the domain (`coding-detail.md`: "Domain must be rich", "All domain validation in domain
layer"), and the usecase is a thin orchestrator that delegates to it (`coding-detail.md`:
"Usecases are orchestrators, not logic holders"). The tests sit one layer out, at the
usecase, and treat the whole domain as a black box — that is what `tdd-rules.md` means by
"Domain files → check against usecase coverage". A test bound to a value object's
constructor breaks the moment that object is split or renamed, which is exactly when the
suite is supposed to prove the refactoring changed nothing.

So a validation rule implemented in `Email` is tested by a usecase scenario named after
the behaviour — `RejectInvalidEmailTest`, not `EmailValueObjectTest`. One test class per
scenario from the story's `tests/01_API_Tests.md`; fakes and Statements live in the
module's support package (`testing/fake/`, `testing/statements/`).

## Conventions

### Backend

| Concern | Convention |
|---------|-----------|
| Test disable marker | `@Disabled("RED: ...")` |
| Not-implemented marker | `throw new UnsupportedOperationException();` |
| Environment file | `infrastructure/.env` |
| Environment setup command | `infrastructure/scripts/setup-ports.sh` |
| External host variable | `BACKEND_EXTERNAL_HOST` |
| Port variable | `BACKEND_PORT` |
| Run command | `infrastructure/scripts/run-backend.sh` (builds `bootJar`, then `java -jar`) |
| Test command | `./gradlew :backend:{module}:test` |
| Acceptance test command | `infrastructure/scripts/test-acceptance.sh` |
| Focused acceptance test command | `infrastructure/scripts/test-acceptance.sh -k {expression}` |
| Coverage report | `build/reports/jacoco/test/jacocoTestReport.xml` (`./gradlew jacocoTestReport`) |
| Health endpoint | `/health` — a hand-written controller, not `/actuator/health`; Actuator is not on the classpath |
| Migration command | `infrastructure/scripts/migrate.sh` (`:backend:adapters:storage:liquibaseUpdate`) |
| Configuration probe | `com.uwords.application.ConfigurationProbe` — binds properties without web, DB, or Redis |
| Architecture check | `./gradlew :backend:architecture:test` |
| Config syntax (Spring YAML) | `${VAR:fallback}` (colon only) |
| Config syntax (compose/shell) | `${VAR:-fallback}` |
| Never | `./gradlew --stop`, and never kill by executable name |

### Frontend

| Concern | Convention |
|---------|-----------|
| Root | `frontend/` (all commands run from here) |
| Stack | React 19 + TypeScript + Vite 6 + Tailwind CSS v4 (`@tailwindcss/vite`) |
| Icons | `lucide-react` |
| Path alias | `@/` → `frontend/src/` |
| Page layout | `src/pages/{Name}Page.tsx` — a page is a thin composition of module components plus routing; it holds no logic and no API calls |
| Module layout | `src/modules/{module}/{components,logic,api,types}/` (modular frontend architecture — `modules/`, not `features/`, wherever a `.claude/tech/react-ts/` template says `features/{feature}`) — one module is one user-facing capability, reusable across pages; `logic/`, `api/`, `shared/api/`, `shared/utils/` each split into `main/` (production) and `test/` (Vitest) like the backend's `src/main` / `src/test`, no module-wide `__tests__/`; where a `.claude/tech/react-ts/` template puts `{Feature}Page.tsx` under `features/{feature}/components/`, this repo puts it under `src/pages/` instead |
| Shared UI | `src/shared/ui/` — generic components used by 2+ modules; `src/app/` holds only composition root, `App.tsx`, `theme.css` |
| Shared API client | `src/shared/api/` — `ApiClient` class (the single `fetch` wrapper) plus `ApiErrorMapper`, which maps every backend status/`ErrorCode` to the one `ApiError` union (`validation-failed`, `unauthorized`, `forbidden`, `not-found`, `conflict` + `retryAfterSeconds`, `unavailable`, reported `unexpected`) and owns status behaviour (409 retry hint, 401 refresh later); a module's `api/` mirrors the backend REST adapter: `{module}.api.ts` client class that only delegates, `endpoints/*.endpoint.ts` (`ApiEndpoint` = `path` + `parse`), `dto/*.dto.ts` classes with `static parse` + `toXxx()` — modules never branch on statuses or invent error kinds |
| File naming | React convention, overriding every kebab-case path in `.claude/tech/react-ts/` and `.claude/templates/refactoring/`: `.tsx` files are PascalCase after the component they export (`PrimaryButton.tsx`, `AuthFlow.tsx`); `.ts` files are camelCase (`apiClient.ts`, `challengeStart.endpoint.ts`, `authScreen.types.ts`, `apiClient.api.test.ts`) — the role suffixes `.logic` / `.api` / `.endpoint` / `.dto` / `.types` / `.fixtures` / `.test` stay lowercase after the dot, only the stem before them is camelCase; no kebab-case source files. Exempt: tool-owned entries `main.tsx`, `vite-env.d.ts`, `index.ts`, config files |
| Shared utilities | `src/shared/utils/` — generic helpers (type guards, text) re-exported from `index.ts`; modules never define private copies |
| Formatting | Prettier 3 (`.prettierrc.json`: semicolons on, single quotes, width 120); `npm run format` / `npm run format:check` |
| Theme stylesheet | `src/app/theme.css` (`@theme` tokens + `@apply` semantic classes) |
| Unit/API-client tests | Vitest 3 + MSW 2; server lifecycle in `src/test/setup.ts`, instance in `src/test/msw-server.ts` |
| Test skip marker | `it.skip` / `describe.skip` with a comment above naming the RED reason |
| API configuration | Required `VITE_API_URL` from `frontend/.env.local` (template `.env.example`) or the deployment environment; never derived from `BACKEND_PORT` |
| Test API URL | `frontend/.env.test` sets `VITE_API_URL=http://api.test` for Vitest/MSW |
| Infrastructure | `frontend/infrastructure/` |
| Local infrastructure environment | `frontend/infrastructure/.env` (generated, gitignored) |
| Environment setup command | `infrastructure/scripts/setup-ports.sh` (from `frontend/`) |
| Port variable | `FRONTEND_PORT` (5173 + repo index) |
| External host variable | `FRONTEND_EXTERNAL_HOST` |
| Install command | `npm install` |
| Run command | `infrastructure/scripts/run-frontend.sh` (from `frontend/`; PID in `infrastructure/run/`, log in `infrastructure/logs/`) |
| Stop command | `infrastructure/scripts/stop-frontend.sh` (from `frontend/`) |
| Typecheck command | `npm run typecheck` |
| Format command | `npm run format` (write) / `npm run format:check` (verify) |
| Build command | `npm run build` |
| Test command | `npx vitest run` |
| Focused test command | `npx vitest run {filter}` |
| Browser E2E | Java 21 + Selenium 4 + JUnit 5 + AssertJ, standalone Gradle project `frontend/e2e/` (own wrapper, not in root `settings.gradle.kts`) |
| E2E root package | `com.uwords.e2e` — where a `.claude/tech/selenium/` template writes `app.e2e.tests.{feature}` / `app.e2e.statements.{feature}`, use `com.uwords.e2e.tests.{feature}` / `com.uwords.e2e.statements.{feature}` |
| E2E base class | `com.uwords.e2e.AbstractUiTest` (`webDriver`, `wait`, `appUrl`; reads `APP_URL`, `E2E_HEADLESS`) |
| E2E scenario annotation | `com.uwords.e2e.Description` |
| E2E test disable marker | `@Disabled("RED: ...")` |
| Acceptance test command | `infrastructure/scripts/test-e2e.sh` (from `frontend/`; requires the dev server running) |
| Focused acceptance test command | `infrastructure/scripts/test-e2e.sh '{ClassName}'` or `'{ClassName}.{method}'` (Gradle `--tests` pattern) |
| Chrome driver | resolved by Selenium Manager; headless by default, `E2E_HEADLESS=false` for a visible browser |
| Never | `pkill node`, `killall node`, `./gradlew --stop` |

### Bot (existing application under adoption)

| Concern | Convention |
|---------|-----------|
| Root | `bot/` |
| Stack | Python 3.12+ + aiogram 3.x |
| Framework lifecycle status | Paused until API/bot responsibilities are divided and redundant bot code is removed |
| Existing source layout | `src/{domain,application,infrastructure,presentation}`; do not create a parallel `src/bot_app/` tree |
| Telegram transport | FastAPI webhook entrypoint at `presentation.bot.main:app` |
| Current persistence | Bot-owned PostgreSQL + Alembic, retained temporarily until API/bot ownership is divided |
| FSM storage | Bot-owned Redis |
| Infrastructure | `bot/infrastructure/` |
| Secret environment | `bot/.env` (local only, gitignored; template: `bot/.env.example`) |
| Local infrastructure environment | `bot/infrastructure/.env` (generated, gitignored) |
| Environment setup command | `infrastructure/scripts/setup-ports.sh` (from `bot/`) |
| Bootstrap command | `infrastructure/scripts/bootstrap.sh` (from `bot/`) |
| Infrastructure start command | `infrastructure/scripts/run-infra.sh` (from `bot/`) |
| Infrastructure stop command | `infrastructure/scripts/stop-infra.sh` (from `bot/`) |
| Migration command | `infrastructure/scripts/migrate.sh` (from `bot/`) |
| Run command | `infrastructure/scripts/run-bot.sh` (from `bot/`) |
| Stop command | `infrastructure/scripts/stop-bot.sh` (from `bot/`) |
| API configuration | Deferred until the API/bot responsibility split; future binding is explicit `API_BASE_URL` |
| Planned unit/API-client tests | pytest + pytest-asyncio under `bot/tests/` after responsibility cleanup |
| Planned bot E2E | Dispatcher-driven tests with a strict API stub under `bot/e2e/` after responsibility cleanup |
| Test command | Unavailable until responsibility cleanup and characterization baseline |
| Logic test command | Unavailable until responsibility cleanup and characterization baseline |
| Focused logic test command | Unavailable until responsibility cleanup and characterization baseline |
| API-client test command | Unavailable until the HTTP API boundary exists |
| Focused API-client test command | Unavailable until the HTTP API boundary exists |
| Handler test command | Unavailable until responsibility cleanup and characterization baseline |
| Focused handler test command | Unavailable until responsibility cleanup and characterization baseline |
| Acceptance test command | Unavailable until responsibility cleanup and characterization baseline |
| Focused acceptance test command | Unavailable until responsibility cleanup and characterization baseline |
