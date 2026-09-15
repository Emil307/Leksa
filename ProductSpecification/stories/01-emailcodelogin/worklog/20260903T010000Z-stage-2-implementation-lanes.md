# 2.1 Запрос кода возвращает challenge и кладёт в очередь готовую заявку — stage-2 implementation lanes

Started: 2026-09-03T01:00:00Z

Outcome: PASS — all five lanes, the seam fix and one coverage follow-up are committed

## Normalization of the approved plan

The five lanes recorded at approval map one-to-one onto architectural execution
boundaries: one use-case behaviour lane, one lane per discovered adapter boundary
(cache, storage, rest), and the composition root. Manifests were re-checked and are
disjoint; no lane writes a path owned by another, and no lane needs another lane's new
output to compile or to run its own focused cycle. Stage 1 contracts are read-only in
every lane.

## Lane checkpoints

| lane | RED | GREEN | owned paths (summary) |
|---|---|---|---|
| usecase | 5752a4d | d3de19f | domain auth kernel + email_code, `usecase/services/auth/start_challenge.py`, `usecase_testing/**` |
| cache | 2cb4edb | fb0f4d0 | `adapter_cache/{client,challenge_store,scripts}.py`, `cache_testing/**` |
| storage | 2117a65 | 05bf01a | `adapter_storage/outbox_queue.py`, notifications-outbox migration, `storage_testing/**` |
| rest | 34a5b42 | 5d06f1a | `adapter_rest/routers/auth.py`, `rest_testing/**` |
| application | a4170a7 | ddba1ca | `application/{system,settings,wiring,main}.py`, `application/tests/test_app_factory.py` |
| seam (coordinator) | — | 63bd872 | `adapter_cache/challenge_store.py` |
| coverage follow-up | — | 0849324 | `application/tests/test_system.py`, `application_testing/**` |

Refactor across the whole range published as the trailing commit of this work unit:
seventeen items merged from the three detector clusters — key-composition and
`CooldownAcquisition` factories in the cache boundary, `StartedChallenge.of` and two
extracted methods in the use case, one shared rejection-message constant, the dead
`Challenge.key_pointer_value`, `CallJournal` moved out of the port-double namespace,
the unobserved state machine dropped from the challenge-store fake, and shared test
client / response-assertion helpers in the rest lane. Nine detector proposals were
rejected on purpose, the Lua redesign and the port retyping among them, because they
change a contract rather than its shape.

Joined verification after the last lane: 34 passed; after the follow-up: 36 passed.
`ruff check backend` clean, `lint-imports` 1 contract kept / 0 broken, no file over 200 lines.

## Acknowledged deviations from the approved manifests

- usecase added a lane-local `services/auth/conftest.py` and an unlisted
  `usecase_testing/fakes/call_journal.py`; both are inside the lane's own test tree.
- application deleted `application/security/system_clock.py`, superseded by the
  listed `application/system.py`. Stories 4 and 5 still name the deleted path in
  `progress.md` and in `token-rotation-contracts-decision.md`; repointing them is
  those stories' work, not 2.1's.
- application added one dependency entry to its `pyproject.toml`.
- cache builds the record key inside Lua rather than passing it as a key argument.
- rest gained `rest_testing/statements/auth.py`, split out of the listed
  `rest_testing/auth.py` under the 200-line cap.

## Seam defect closed by the coordinator

`RedisChallengeStore.__init__` defaulted its client to `None` and `wiring.py` built
the store with no argument, so the first `eval` in production would have raised
`AttributeError`; `get_redis()` had no caller anywhere. No lane owned the seam — the
cache lane always injects a client, the application lane treated the constructor as a
frozen surface. Closed in 63bd872 by mirroring `OutboxNotificationQueue`.

## Findings carried out of Stage 2 (not fixed here)

- `adapter_storage/models/__init__.py` does not export `UserEntity`, so
  `Base.metadata` in `migrations/env.py` omits `auth.t_users` and autogenerate would
  propose dropping it. Inherited from story 0002, outside 2.1's manifests.
- `DISCARD_STARTED_CHALLENGE` has no owning scenario anywhere in the plan; the
  compensating path is exercised only by the usecase fake.
- `get_email_sender()` in `wiring.py` has no caller; email delivery is unbuilt.
- Infrastructure 4.1's table omits `AUTH_CHALLENGE_CODE_LENGTH` and
  `AUTH_CHALLENGE_REPLAY_WINDOW_SECONDS`, and its JWT-secret row cannot fire because
  `AuthTokenSettings` is not a field of `Settings`.
