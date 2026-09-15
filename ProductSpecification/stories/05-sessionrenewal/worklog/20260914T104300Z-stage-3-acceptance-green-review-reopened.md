# 2.1 Действующая сессия получает новую пару токенов — stage-3 acceptance GREEN + review (после переоткрытия)

Started: 2026-09-14T10:43:00Z

Outcome: completed

- Предпосылка: Stage 2 переоткрытых полос закрыт коммитом `c0c284f`
  (запись `20260914T102200Z-stage-2-implementation-lanes-reopened.md`).
- Backend поднят из свежего jar (`run-backend.sh`, порт из `infrastructure/.env`), `/health` → 200.
- Лейны запущены одновременно: acceptance GREEN (снят только `@pytest.mark.skip` и неиспользуемый
  импорт в `acceptance/tests/backend/auth/test_token_refresh_acceptance.py`) ‖ `agent-review-agent`
  ‖ `premortem-agent` над диапазоном `3fc278d..HEAD` (+ `3fc278d`). Первый батч
  (`20260914T091551Z-stage-3-acceptance-green-review.md`) потреблён ранее; его NEEDS_CYCLE
  (уникальный claim) поглощён переоткрытием, SAFE-фикс `SessionRepository` отложен до GREEN.
- Acceptance GREEN: целевой `TestTokenRefreshAcceptance` — 1 passed; полный прогон
  `-q -p no:cacheprovider` — 125 passed, 19 skipped (было 124/20: включён ровно этот тест).
  Лейн не переоткрывался.

## Вердикты ревью (батч Stage 3, потреблён один раз)

- agent-review: CONCERNS — 3 находки, все SAFE.
  1. `c0c284f` перевёл `stage-3` в `[~]` у всех 23 сценариев (глобальный sed) — план
     повреждён; фикс: вернуть `[ ]` всем, кроме 2.1 (`grep -c '\[~\]'` = 1). Применено.
  2. Контракт `jti`/`aud` не выражен в acceptance: `auth_statements.assert_session_carries_identifier_and_both_tokens`
     проверял только `sub/sid/exp`, `assert_both_tokens_are_new` сравнивал строки JWT. Применено
     (утверждения `jti` — UUID, `aud == API_AUDIENCE`; ротация сравнивает `jti`).
  3. Мёртвый `acceptance/clients/mail/` (после `3fc278d` ссылок нет). Удалён.
  Проверено без замечаний: порядок `ids.newId()` в `VerifyAuthChallengeService`, строковый `aud`,
  `withExpiresAt(Instant)` без дрейфа секунд.
- premortem: CONCERNS — 1 CREDIBLE (SAFE) = находка 2 agent-review (тот же фикс); 2 NO_FIX;
  4 REMOTE (уже защищены unit/usecase/acceptance-тестами).
  - NO_FIX «старый access-токен действует до `exp` после refresh»: `jti` не персистится,
    `ActiveSession.authorizes` сверяет `sid/sub/exp`; обязательства истории нет
    (`interview.md:82`) — admission-test правило 5 не выполнено, записано без чекбокса.
  - NO_FIX «расходящийся `JWT_SECRET` между инстансами»: операционная конфигурация, дельтой
    не затронута.
- Отложенный SAFE из первого батча: `SessionRepository.findActiveByRefreshToken` —
  `getResultStream().findFirst()` → `setMaxResults(SINGLE_ROW).getResultList().stream().findFirst()`.
  Применено; storage 31 passed.
- NEEDS_CYCLE / NEEDS_CLARIFICATION: нет. Чекбокс `resolve stage-3 cycle proposals` не нужен.
- Full acceptance guard на «выпущенный токен открывает `/profile`» — плановый следующий юнит
  Tier 1 Integration 1.1, новых шагов не вносится.
