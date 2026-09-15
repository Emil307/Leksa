# Stage 3 — acceptance GREEN + review (Story 4, scenario 1.1)

Invocation: `/continue story 4`
Outcome: `passed`
Range reviewed: `e849029..5ed055f` (immutable stage 1+2)

## Acceptance

Marker removed from `test_profile_read_acceptance.py`, nothing else touched.
Suite: 2 passed, 2 skipped (skips belong to stories 1 and 5). Commit `b2a55b4`.

## Verdicts

- agent-review: BLOCK — 8 findings (3 carried over, 5 new)
- premortem: CONCERNS — 4 credible incidents, 4 remote

## SAFE — applied inline

1. `domain/auth/user/gender.py` — `Gender.parse` had no caller after `a151454`
   moved unknown-gender refusal into `UserRepository.find_by_id`. Deleted with
   its now-unused import and message constant.
2. `repositories/active_session.py`, `repositories/user.py` — the mapper call sat
   outside the `try` that translates storage failures. Correct only because
   `expire_on_commit=False`; an invariant no test pins. Moved inside.
3. `acceptance/statements/auth_database.py` — hardcoded connection fallbacks let
   a run from repo index >= 1 insert rows into index 0's database. Now reads every
   setting through `required_value`, matching `access_token.py`.
4. `infrastructure/.env.example` — gained `JWT_SECRET`, without which a freshly
   templated environment cannot import `application.main` at all.
5. `application_testing/statements/app_factory.py` — `raise_app_exceptions=False`
   dropped from the shared transport, so a future non-2xx assertion cannot pass on
   a swallowed traceback.

Checks after the fixes: backend 60 passed, acceptance 2 passed / 2 skipped,
ruff clean, import contracts 1 kept 0 broken.

## Admitted NEEDS_CYCLE — proposed, awaiting consent

**P1. A PostgreSQL command timeout answers 500 instead of the uniform 401.**
Both repositories catch `SQLAlchemyError` only; asyncpg raises `asyncio.TimeoutError`
on `command_timeout`, which SQLAlchemy's asyncpg dialect does not translate.
Observed: premortem drove the real stack and got `status: 500 body: Internal Server
Error`. Violates the ADR edge-case row naming timeout an explicit 401/`storage`
case and `endpoints.md`'s uniform-401 rule. Fix changes behavior, so it needs a
red test first: a session raising `TimeoutError` asserting `UnavailableException`
in both repositories.

**P2. The served OpenAPI document contradicts the approved contract.**
`routers/profile.py:21` declares no `responses=` and no security dependency.
Observed against the running backend: `responses: ['200']`, `security on op: None`,
`securitySchemes: []` — the document advertises the guarded read as an
unauthenticated 200-only endpoint. Stage 1 approved `profile_get.yaml` with
`security: bearerAuth` and a `401`. `assert_profile_route_is_mounted_as_a_guarded_read`
asserts nothing about the guard despite its name.

## Failed admission — disposition without a checkbox

- **Alembic floor blocks the mixed deployment.** `0001_auth_sessions` calls
  `create_table` without `if_not_exists` while `0002` uses it, so `upgrade head`
  fails with `DuplicateTableError` on a database that already has `auth.t_sessions`
  — the exact database the `LEGACY_SESSION` branch exists for. Observed. Outside
  scenario 1.1's obligation; the ADR already routes it to Infra 1.1. Escalated as
  a release concern: do not deploy onto a pre-existing auth schema until it lands.
- **`setup-ports.sh` cannot backfill a key into an existing `.env`.** Only `FORCE=1`
  recovers, and it rotates the secret, invalidating every issued token. Outside the
  scenario's obligation (rule 5). Named follow-up; `.env.example` now at least
  documents the key.
- **Naive `created_at` shifted by the host offset.** `schemas/profile.py:48` calls
  `astimezone(UTC)` on a possibly naive value while the session mapper defends
  against exactly that. Reasoned, not observed, and only reachable on a database
  the alembic floor cannot migrate. Recorded.
- **Unbounded pool wait.** Two connections per guarded request, no `pool_timeout`
  or `max_overflow`, so saturation logs a valid user out after ~30 s. Outside the
  obligation; named follow-up into the planned Infra 2.1 / Security work.

## NO_FIX — reported, dropped

- No clock leeway, so a few seconds of inter-instance skew can refuse a token at
  its exact boundary; self-heals on refresh, guard costs more than the incident.
- Story 5 will issue tokens without `aud`/`jti`, which this guard refuses. Already
  a recorded ordering requirement in the ADR; a cross-story CI check costs more.
- `@lru_cache` in `wiring.py` is not an in-memory-state violation: only stateless
  services and a config snapshot are cached, never an auth decision.
- Missing `WWW-Authenticate: Bearer` — dropped in the earlier pass; changing the
  response bytes would move the uniform-401 contract 1.1 pins. Belongs to Security.

<!-- lanes: acceptance=PASS; agent-review=BLOCK; premortem=CONCERNS -->

## Consent — 2026-09-03

Invocation: `resolve stage-3 cycle proposals`. User decision: "вторую проблему
решаем остальные скип".

- **P2 accepted.** Written as Tier 2 Backend scenario `4.1 Опубликованный контракт
  описывает чтение профиля как защищённое` in `tests/01_API_Tests.md`, with its
  four-step staged block carrying `<!-- review-origin: boundary -->`. Tier 2 per
  "Mid-cycle findings default to Tier 2": the guard itself works for the primary
  user; the served document, not the enforcement, is wrong. Placed at the end of the
  Tier 2 backend section, so the cursor stays on `harvest` and tier-first order holds.
- **P1 declined.** The PostgreSQL command timeout keeps answering 500. No scenario,
  no checkbox, no test. Recorded here as the standing gap: the uniform-401 rule in
  `endpoints.md` and the ADR timeout row are knowingly unmet for that one path.
- The four failed-admission dispositions and the four NO_FIX drops above stay as
  recorded; the decision changed nothing about them.

Scenario 1.1's block closes with this commit. Its review batch was consumed at
stage 3 and is not dispatched again.

<!-- consent: P2=accepted->tier2-backend-4.1; P1=declined -->
