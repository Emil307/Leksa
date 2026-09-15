# 2.1 Запрос кода возвращает challenge и кладёт в очередь готовую заявку — approve stage-1 contracts

Started: 2026-09-03T00:00:00Z

Outcome: completed

- Decision: APPROVED by the user. Stage 1 contracts are frozen and read-only for Stage 2;
  the approval checkbox closes and `stage-2 implementation lanes` becomes current.
- Contracts approved are the post-restructure shape, not the shape committed at design
  time (`9235fc1`). Six material differences were presented and accepted:
  1. `Challenge` holds `ChallengeSecret`, not `VerificationCode` — the kernel no longer
     knows about codes.
  2. The secret is issued by the strategy (`ChallengeStrategy.issue_secret()`), not by
     `StartAuthChallengeService`.
  3. `CodeGeneratorPort` was deleted from usecase; `CodeGenerator` is a domain protocol.
  4. `code_length` moved from `ChallengePolicy` to `CodePolicy`.
  5. `ChallengeStrategy.notification_for` and `NotificationQueuePort.enqueue` are typed
     `OutboundNotification`, not `OutboundEmail`.
  6. Package layout: `domain/common/`, `domain/auth/{challenge,code,session,user,email_code,failure}`,
     `usecase/ports/{auth,notifications,system}`, `usecase/caller.py`.
  Rationale for 1-5 is in `decisions/challenge-start-contracts-decision.md`; the layout
  convention is in `.claude/rules/coding-rules.md`, "Domain Package Layout".
- Stage 2 prerequisite applied by the coordinator before dispatch, as the plan required —
  unassigned to any lane so no lane depends on another:
  - `requirements.txt`: `-e backend/adapters/cache` added after storage.
  - `.importlinter`: `adapter_cache` added to `root_packages` and to the adapter layer line.
  - `pyproject.toml`: `backend/adapters/cache/tests` added to `pythonpath`.
  - `uwords-adapter-cache` and `redis>=5.0` installed into `.venv`; `adapter_cache` now imports.
- Checks: ruff (backend, acceptance, frontend) — all checks passed; lint-imports — 1 kept,
  0 broken over 120 files / 128 dependencies; `pytest backend` — 12 passed, 0 failed;
  `pytest acceptance --collect-only` — 4 collected.
- Note: `ruff check .` at the repository root reports 489 errors, all from the untracked
  `bot/` tree, which is outside this story and outside the tracked working set.
- Next: five disjoint Stage 2 lanes — usecase, adapter-cache, adapter-storage, adapter-rest,
  application — per the `stage-2-plan` block in `progress.md`.
