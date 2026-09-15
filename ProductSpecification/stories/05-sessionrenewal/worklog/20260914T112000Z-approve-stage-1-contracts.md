# 1.1 Успешный запрос согласованно обновляет хранилище и выпускает JWT — approve stage-1 contracts

Started: 2026-09-14T11:20:00Z

Outcome: completed

- Decision: утверждено. Источник решения — сквозная инструкция пользователя «полностью сделай
  сценарий Integration Scenarios 1.1» (запрос на прогон всех стадий без пауз); отдельной
  фразы «approve» не было — координатор трактует инструкцию как предварительно выданное
  согласие и фиксирует это здесь, чтобы решение можно было оспорить.
- Reviewed: `TestSessionRotationConsistencyAcceptance` — ALREADY_GREEN, два кейса после
  test-review (ротация: строка + JWT; повтор старого токена: 401 + строка неизменна),
  четыре Then-клаузы по реестру записи
  `20260914T110500Z-stage-1-acceptance-red-contract-design.md`.
- Frozen: новых контрактов нет — поверхности заморожены записью 2.1
  (`20260903T000000Z-approve-stage-1-contracts.md`) и дополнением
  `decisions/token-rotation-contracts-decision.md` от 2026-09-14 (`jti`/`aud`, чтение строки
  сессии через `AuthDatabase`).
- Lane plan: NO_DELTA — Stage 2 помечается `[S]` (ALREADY_GREEN + NO_DELTA), полосы не
  диспетчеризуются.
- Stage-1 commits: acceptance `49fa282` (refactor следует отдельным коммитом).

<!-- stage-1-approval: granted; stage-2 advanced -->
