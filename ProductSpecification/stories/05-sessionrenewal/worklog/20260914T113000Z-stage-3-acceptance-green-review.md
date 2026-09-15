# 1.1 Успешный запрос согласованно обновляет хранилище и выпускает JWT — stage-3 acceptance GREEN + review

Started: 2026-09-14T11:30:00Z

Outcome: completed

- Контекст: Stage 1 `49fa282` (ALREADY_GREEN, тест включён), approval `9a842f3`, Stage 2 `[S]`.
  Дельта remove-marker отсутствует — GREEN подтверждается прогоном включённого теста.
- Полосы Stage 3 (параллельно): acceptance GREEN (targeted + полный suite) ‖ `agent-review-agent`
  ‖ `premortem-agent` над диапазоном `98d0e96..HEAD` (Stage 1 + approval + refactor).

## Acceptance GREEN

- Дельты remove-marker нет: `TestSessionRotationConsistencyAcceptance` включён с `49fa282`.
- Refactor Stage 1 закоммичен отдельно `a7439c5` (20 применено, 4 NO ACTION: A55 pass-through
  исчез после A21; A8 inline `mint_access_token` в двух диагностиках нарушил бы линейный рецепт;
  A1 общий helper для шести `sign_in_*` неочевиден; D-A7 константы стартовой конфигурации —
  ключи таблицы из 8 переменных). Полный прогон после refactor: 127 passed / 19 skipped.
- Targeted `SessionRotationConsistency`: 1.1 GREEN (`1 passed` в Stage 1, `7 passed / 1 skipped`
  вместе с TokenRefresh/TokenLifetime/SameSessionReplay после review-fix).

## Review (диапазон `98d0e96..HEAD` + рабочее дерево refactor)

- premortem — **PASS**, credible=0. Шесть инцидентов, все REMOTE/NO_FIX: (1) ротация не продлевает
  срок — гард на usecase/adapter с фиксированными часами; (2) чтение строки до коммита — `@Transactional`
  завершается до ответа; (3) верхняя граница окна `responded+TTL` vs `floor(responded)+TTL` — для
  int `exp` эквивалентно; (4) `updated_at` не в `StoredSessionRow` — покрыт adapter-тестом;
  (5) `OutboxDatabase` в `AuthStatements` — одно короткоживущее соединение на тест;
  (6) refresh-токены в plaintext — предмет отдельной истории, не гарда. Approval из сквозной
  инструкции пользователя отмечен как оспоримое решение — NO_FIX.
- agent-review — **CONCERNS**, 1 находка, SAFE: клауза «новый срок» доказывалась только
  вероятностно (логин и ротация в одну секунду дают равные `expires_at` из-за
  `SessionPolicy.truncate`). Применено: `LiveStoredSession.stored` возвращён,
  `wait_for_the_second_after(created_at)` (≤1 с) перед ротацией, строгий
  `stored_after.expires_at > stored.expires_at`; ADR-дополнение — `SELECT` читает и `created_at`.
  Targeted 7 passed / 1 skipped. Расхождение с premortem (инцидент 1, «sleep дороже») решено в
  пользу детерминированного сквозного гарда: ожидание ≤1 с в одном тесте.
- NEEDS_CYCLE / NEEDS_CLARIFICATION: нет. Quiz не требовался.
