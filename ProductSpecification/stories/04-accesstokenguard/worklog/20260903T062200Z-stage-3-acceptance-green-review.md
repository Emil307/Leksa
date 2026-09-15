# 1.1 Пользователь с действующей сессией получает всю свою запись — stage-3 acceptance GREEN + review

Started: 2026-09-03T06:14:00Z

Outcome: failed — acceptance GREEN red; Stage 3 reset to pending, Stage 2 reopened

- Acceptance GREEN: 1 failed, 3 deselected. `TestProfileReadAcceptance` answered HTTP 500 instead of 200.
- Root cause: `SystemClock.now()` raises `NotImplementedError`; `wiring.py:33` injects it as the production clock and `AuthenticateRequestService.authenticate` calls it on every guarded request.
- Probe (temporary `datetime.now(UTC)` body, reverted, never staged): acceptance 1 passed. The stub is the only blocker; the whole 1.1 path is green through HTTP once the clock works.
- Ownership conflict: Story 4 froze `SystemClock (read-only, owned by Story 5)`; the body of `now()` sits in Story 5's application lane, whose stage-2 is still `[~]`. Story 4 cannot ship independently under that freeze — this is a Stage 1 contract defect, not a lane implementation defect.
- Working tree restored: probe reverted, `@pytest.mark.skip(reason=RED_REASON)` re-applied to the acceptance target.

## Review verdicts

- agent-review: BLOCK — 5 findings (1 blocking, 2 CONCERNS, 2 low).
- premortem: BLOCK — 3 credible incidents (SystemClock stub 500; `.env` without `JWT_SECRET`; alembic floor). The agent died on an API error immediately after logging its verdict; the full report was lost and must be re-run.
- Triage NOT run: `parallel-backend-stages.md` applies findings only after acceptance succeeds.

## Findings carried to the reopened Stage 2 / Stage 1

1. NEEDS_CYCLE (blocking, both passes) — `application/security/system_clock.py`: production clock is a stub. Any syntactically valid signed token yields 500 while a malformed header yields 401, which is itself an oracle. No test exercises the real wired clock: usecase uses a fake clock, rest uses `FakeAuthenticateRequestService`, `test_app_factory` never requests the route.
2. NEEDS_CYCLE — `repositories/active_session.py:22`, `repositories/user.py:23` catch only `SQLAlchemyError`. The engine sets `command_timeout`, and asyncpg's `asyncio.TimeoutError` is not translated into a `SQLAlchemyError`, so a PostgreSQL timeout escapes as 500. The ADR requires a uniform 401 with reason `storage` on timeout. Existing tests simulate failure with `OperationalError` only.
3. SAFE — `infrastructure/scripts/setup-ports.sh` writes `JWT_SECRET` inside the heredoc that an existing `.env` short-circuits, so machines set up before this commit get no `JWT_SECRET`: backend boot fails and the acceptance suite fails on `required_value(JWT_SECRET_VARIABLE)`. Fix is to append the missing key before the early exit rather than requiring `FORCE=1`, which would rotate the secret.
4. SAFE — `acceptance/statements/auth_database.py` falls back to hardcoded `DB_PORT=5432` and `uwords/uwords`, so an unexported `DB_PORT` makes the suite INSERT rows into another repo instance's database. Fix is to use `required_value` as `access_token.py` already does.
5. NO_FIX — 401 carries no `WWW-Authenticate: Bearer` and the route declares no OpenAPI security scheme. Changing the response bytes would move the uniform-401 contract that 1.1 pins; belongs with the Tier 2 Security scenarios.

<!-- lanes: usecase=PASS; adapter-storage=PASS; adapter-rest=PASS; adapter-application-security=INVALIDATED -->
