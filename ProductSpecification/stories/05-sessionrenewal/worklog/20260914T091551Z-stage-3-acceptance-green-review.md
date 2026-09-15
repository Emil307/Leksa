# 2.1 Действующая сессия получает новую пару токенов — stage-3 acceptance GREEN + review

Started: 2026-09-14T09:15:51Z

Outcome: completed

- Триаж: диапазон Stage 1+2 содержит исходники (`backend/**`, `acceptance/**`) → оба
  ревью-прохода RUN. Диапазон: Stage 1 `688d65d`, `9d8ab7e`, `44ad11f`; Stage 2
  `af4fd9b..7f9d941` (изменённые пути — `git diff --name-only b4e9f8e..7f9d941`).
- Бэкенд: на порту инстанса работал jar от 10 сентября (старее коммитов Stage 2);
  остановлен через `stop-backend.sh`, пересобран `bootJar`, запущен заново.
- Acceptance GREEN: маркер с `TestTokenRefreshAcceptance` снят, прогон
  `test-acceptance.sh -k TestTokenRefreshAcceptance` → **1 failed**: `given_live_session`
  ждёт код входа в MailHog (`mailbox.await_login_code`), а почтовый ящик пуст.
- Причина: продукт с Story 1 (4.6, `challenge-start-contracts-decision.md`) кладёт письмо в
  `notifications.t_outbox` и не отправляет SMTP (`SmtpSender` не используется ни одним
  бином); все включённые тесты читают код через `OutboxDatabase.queued_code_for`
  (`AuthStatements.request_code_and_capture`). `given_live_session` написан 16 августа
  (Stage 1, `688d65d`) до перехода на outbox — устаревшая предпосылка теста, полосы Stage 2
  не замешаны (POST /auth/challenge/start ответил 200, до `/auth/token/refresh` тест не дошёл).
- Действие: маркер возвращён с точной причиной RED (единственное разрешённое изменение
  GREEN-полосы); production-код и Statements не тронуты. Stage 3 остаётся `[~]`.
- Требуемое исправление (лежит в acceptance-полосе Stage 1, а не в Stage 2):
  переписать `AuthStatements.given_live_session` на путь через `OutboxDatabase`
  (по образцу `request_code_and_capture`), затем повторить Stage 3.
- Полный acceptance-прогон на пересобранном бэкенде: 124 passed, 20 skipped —
  Stage 2 ничего из уже включённых тестов не сломал.
- Сброс: замешана acceptance-полоса Stage 1 (Statements), а не полоса Stage 2 — `stage-1`
  возвращён в `[~]` с областью «только acceptance-полоса»; approval и Stage 2 остаются
  `[x]` (контракты и реализация не затронуты); `stage-3` → `[ ]`.

## Ревью (диапазон Stage 1+2, потреблён один раз)

- agent-review: **CONCERNS**; premortem: **PASS** (7 воображаемых инцидентов, 0 credible).
- Повторный Stage 3 после починки `given_live_session` ревьюит только дельту
  acceptance-полосы (коммит починки), не весь диапазон заново.

### NEEDS_CYCLE — допущено (все пять правил admission-теста)

Идентичный access-JWT при login и refresh в одну и ту же секунду.
`JwtAccessTokenIssuer.issue` подписывает только `sub`, `sid`, `exp` (`exp` усечён до
секунды); `Session.accessTokenClaims` / `SessionPolicy.accessExpiryAt` не добавляют
ничего уникального. Login (`VerifyAuthChallengeService:116`) и refresh
(`RefreshSessionTokensService:44`) в одной секунде → байт-в-байт одинаковый токен →
`assert_both_tokens_are_new` (Stage 1, `688d65d`) падает недетерминированно.
Наблюдение: два `JWT.create()` с теми же claims через 300 мс дают `identical=true`
(java-jwt 4.4.0, воспроизведено в scratchpad `Repro.java`). Обязательство:
`05_SessionRenewal.md` поток п.2/п.4 («новая пара») и Stage 1 acceptance-тест.
Предложение цикла: добавить `jti` (UUID через порт генератора идентификаторов) в
`AccessTokenClaims`, выставлять в `JwtAccessTokenIssuer`; red→green в usecase-полосе +
application-полосе; дополнить `decisions/token-rotation-contracts-decision.md`.
Не вносится в план без явного согласия; checkpoint `resolve stage-3 cycle proposals`
добавляется при завершении Stage 3 (ссылка на эту запись).

### SAFE — отложено до успешного acceptance

`backend/adapters/storage/.../SessionRepository.java:42-46` — `getResultStream().findFirst()`
не закрывает Hibernate-stream; замена на `.setMaxResults(SINGLE_ROW).getResultList().stream()
.findFirst().map(SessionMapper::toDomain)`. По шаблону SAFE-фикс применяется только после
join с успешным acceptance → лендится в `review-fix:` повторного Stage 3.

### NO_FIX

- `SessionRefreshRequestDto` с `@JsonIgnoreProperties(ignoreUnknown=true)` при контракте
  400 на лишние поля — закрывается Tier 2 Security 1.1 (та же конвенция у
  `ChallengeVerifyRequestDto` из Task 2 — решать там).
- Коллизия сгенерированного refresh-токена → 500 и токен чужой сессии в `log.error` —
  256 бит энтропии, гвард дороже инцидента.
- `RefreshToken.of` на сгенерированном токене даёт 400 при дефекте генератора — принято.
- `PersistenceException` в `SessionRepository` не оборачивается в `UnavailableException`
  → 500 вместо 503 — закрывается Infra 1.1/1.3.
- Гонка двух инстансов за один refresh-токен — условный `UPDATE` + уникальный индекс;
  чёрный ящик в API 3.3, Integration 1.2/1.3.
- Подписанный JWT проигравшего гонку не сохраняется и не логируется — Security 3.2.
- `updated_at` не усечён до секунды в отличие от `expires_at` — вне контрактов истории.
