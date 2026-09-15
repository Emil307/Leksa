# 2.1 Действующая сессия получает новую пару токенов — stage-1 acceptance RED + contract design (reopened)

Started: 2026-09-14T09:41:49Z

Outcome: completed

- Область: только acceptance-полоса (Statements `given_live_session` → `OutboxDatabase`),
  по записи `20260914T091551Z-stage-3-acceptance-green-review.md`. Дизайн-полоса
  (`44ad11f`), approval и Stage 2 не переоткрываются.
- Бэкенд на порту инстанса — jar от `7f9d941`, /health 200, не перезапускался.
- red-agent (acceptance): `given_live_session` переведён на `OutboxDatabase` через
  `request_code_and_capture`; фикстуры `mailbox`/`mailbox_http_client` удалены как мёртвые.
  Проверка с временно снятым маркером: логин пройден, refresh 200, id сессии прежний,
  refresh-токен новый — **1 failed** на `assert_both_tokens_are_new`: access-токен
  побайтно равен прежнему (два прогона, 0.44s/0.30s — детерминированно, не флейк).
  Маркер восстановлен с этой причиной; с маркером: 1 skipped, 143 deselected.
- Predicted failure: ALREADY_GREEN с оговорённым риском `assert_both_tokens_are_new`.
  Actual: AssertionError «rotation must issue a new access token, the previous one came
  back unchanged». Comparison: после прогона 1 прогноз уточнён, прогон 2 совпал.
- /test-review: A — 1 (truthiness на access-токене → разбор claims `sub`/`sid`/`exp`);
  P — 2 исправлено (тест-класс знал `OutboxDatabase`/`AuthStatements` → compound given
  `SessionRefreshStatements.given_live_session()`), P-16 (чтение кода из БД) — паттерн
  набора со Story 1, не трогали; S — 1 (дубль блока «UUID + оба токена» поднят в
  `AuthStatements`, `ChallengeVerifyStatements` делегирует). Попутно удалён дубль
  фикстуры `session_refresh_statements` в `fixtures/challenge_start_fixtures.py`.
- Tests: target 5 passed, 1 skipped (маркер), 138 deselected; полный набор
  124 passed, 20 skipped (дважды: после red-agent и после фиксера).
- Вывод для плана: дефект теперь наблюдён и лежит в Stage 2 — `JwtAccessTokenIssuer`
  подписывает только `sub/sid/exp` с секундной точностью, login и refresh в одну секунду
  дают идентичный access-JWT (обязательство: спека п.2/п.4 «новая пара», Stage 1 тест).
  По шаблону Stage 3 сбрасываются замешанные полосы Stage 2: usecase (claims —
  `AccessTokenClaims`/`Session.accessTokenClaims`, файлы в манифесте usecase-полосы) и
  application (`JwtAccessTokenIssuer`). Чекпоинты `usecase=d985d31`,
  `application=NO_DELTA` из записи `20260913T192310Z` недействительны; rest и storage
  остаются PASS. Предложение NEEDS_CYCLE из записи `20260914T091551Z` этим поглощено —
  отдельный consent-checkpoint не нужен.
- `acceptance/clients/mail/mailhog_client.py` больше никем не импортируется — кандидат
  на удаление в /refactor этой полосы.
