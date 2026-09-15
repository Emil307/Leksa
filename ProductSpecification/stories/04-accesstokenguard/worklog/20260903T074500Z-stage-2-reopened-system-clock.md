# Stage 2 reopened — adapter-application-security (Story 4, scenario 1.1)

Invocation: `/continue story 4`
Outcome: `passed`
Range: `98468d9..HEAD`

## Trigger

Stage 3 acceptance GREEN failed with a 500 (record
`20260903T062200Z-stage-3-acceptance-green-review.md`). Root cause was the
stage-1 frozen surface `SystemClock (read-only, owned by Story 5)`: its `now()`
raised `NotImplementedError` while wired as the production clock, and Story 5's
stage-2 is still `[~]`. That is a stage-1 contract defect, not a lane defect.

## Contract change

The user transferred ownership of `SystemClock` to Story 4 and lifted the
freeze. The coordinator amended the `stage-2-plan` manifest: the file left
`frozen-surfaces` and entered this lane's `writes` together with its tests.

Cross-story note: Story 5's application-lane manifest still lists
`system_clock.py: body of now()`. That lane will now find the body already
present. It is a no-op for Story 5, not a conflict, but Story 5's manifest
should be reconciled when its stage-2 resumes.

## RED

Prediction and observation matched on all four cases: three
`NotImplementedError` from `system_clock.py:6`, and `AssertionError` with the
guarded route answering 500 instead of 401.

The guard the review named is now closed in-process, without database or
network: the real application is composed through `create_app()`, and a
correctly signed token with a passed `exp` reaches the clock and stops there
per the frozen refusal ordering.

## Test review

Four fixes applied: opaque tuple assertion split into value assertions on
`utcoffset()`/`tzname()`; the 5-second tolerance dropped in favour of the exact
`taken_before <= reading <= taken_after` bracket; fake constructor
initialisation replaced by class-level annotations; Given/When/Then order
restored in the new class. Skip markers untouched.

Left standing with reasons: no `valid token -> 200` counter-case (the
`application` unit harness has no storage), and pre-existing tuple comparisons
outside the reviewed delta.

## GREEN

`SystemClock.now()` returns `datetime.now(UTC)`. Signature matches the frozen
`ClockPort.now`.

## Checks

- backend suite: 60 passed, 0 failed, 0 skipped
- `ruff check backend/application`: clean
- import contracts: 1 kept, 0 broken
- `system_clock.py` coverage: 100%

## Carried forward into stage 3

Findings 2, 3 and 4 of the previous agent-review are still open and unfixed;
triage never ran because acceptance never succeeded:

- storage repositories catch only `SQLAlchemyError`, so an asyncpg command
  timeout escapes as 500 instead of the uniform 401 with reason `storage`
- `setup-ports.sh` writes `JWT_SECRET` inside the heredoc an existing `.env`
  short-circuits, so machines set up earlier boot without it
- `acceptance/statements/auth_database.py` falls back to hardcoded connection
  values and can write into another repo instance's database

`premortem` must be re-run at stage 3: its previous report was lost to an API
error after it logged `verdict=BLOCK credible=3`.

<!-- lanes: adapter-application-security=PASS -->
