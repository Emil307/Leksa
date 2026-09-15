# 1.1 Успешный запрос согласованно обновляет хранилище и выпускает JWT — stage-1 acceptance RED + contract design

Started: 2026-09-14T11:05:00Z

Outcome: completed

- Контекст: Tier 1 Integration 1.1 (`tests/06_Integration_Tests.md`, hz-01). Сценарий 2.1 закрыт
  (`10be876`, `98d0e96`): ротация, `jti`/`aud`, условный `UPDATE` уже в продукте. Ожидание:
  acceptance-полоса даст ALREADY_GREEN либо RED на клаузе о строке хранилища / старом токене.
- Backend поднимается из свежего jar (`run-backend.sh`, порт из `infrastructure/.env`).
- Полосы Stage 1 (непересекающиеся):
  - acceptance RED (`red-agent`, layer acceptance): новый тест-класс + Statements в
    `acceptance/`; контракты и скелеты не трогает.
  - contract design (read-only анализ): проверка, что usecase/порты/адаптеры уже покрывают
    четыре Then-клаузы; выдаёт Stage 2 lane plan либо NO_DELTA; acceptance не трогает.

## Результат полос

- acceptance RED — **ALREADY_GREEN**. `TestSessionRotationConsistencyAcceptance`
  (`acceptance/tests/backend/auth/test_session_rotation_consistency_acceptance.py`), один кейс
  `test_should_rotate_storage_row_and_jwt_consistently`, маркер skip не ставился.
  Предсказание = факт: `1 passed` (targeted), стабильно ×3 вместе с 2.1.
  Новое: `statements/session_rotation_consistency_statements.py`, `statements/stored_session_row.py`,
  `clients/application/dto/auth/session_refusal_dto.py`; правки: `auth_database.py`
  (`SELECT_SESSION_ROW`, `stored_session_row`), `auth_client.py`
  (`refresh_session_capturing_refusal`), `conftest.py` (фикстура).
- Реестр клауз: (1) прежний id + новая пара — Statements 2.1; (2) та же строка хранит новый
  refresh-токен и срок в окне `[trunc(requested)+TTL, responded+TTL]`, строка одна;
  (3) HS256 под `JWT_SECRET`, `sub`/`sid` прежние, GET /api/v1/profile → 200 c тем же `id`;
  (4) старый токен → 401 с единым конвертом, строка до/после без изменений.
  Строгое «срок позже прежнего» отвергнуто: домен усекает до секунд (`SessionPolicy.truncate`),
  логин и ротация в одну секунду дали бы флаки.
- contract design — **NO_DELTA**. Все четыре Then-клаузы обеспечены кодом 2.1:
  `RefreshSessionTokensService.refresh` → `SessionRepository.rotateRefreshToken` (один JPQL
  `UPDATE` с `refreshToken`+`expiresAt`, rowcount), `JwtAccessTokenIssuer` (`sub,sid,jti,exp,aud`),
  `AccessTokenInterceptor` → `ActiveSession.authorizes`, `GlobalExceptionHandler` → 401.
  Новых контрактов/скелетов/миграций не требуется; `<!-- stage-2-plan -->` не выпускается.
  Отмечено вне области: `SessionRefreshRequestDto` игнорирует неизвестные поля, тогда как ADR
  требует 400 `VALIDATION_FAILED` — предмет Tier 2 API-сценария, не 1.1.
- Stage 2: по правилу ALREADY_GREEN + NO_DELTA — `[S]` после approval.

## Test-review (детекторы A/P/S → фиксер)

- Применено 12 находок, 14 файлов: A-5/7 (claims `aud`/`exp` в проверке JWT), A-27 (структурное
  сравнение вместо пофилдовых assert), A-7 (профиль сверяется целиком, не только `id`),
  A-3 (избыточное `expires_at >=` снято — окно единственный guard), P-13 (инъекция
  `SessionRefreshStatements`, составной `assert_rotation_answered_with_same_session_and_new_pair`),
  P-29 (кейс разделён на два метода, `given_rotated_live_session`), S-11 (единый конверт 401 →
  `wire_contract.assert_unified_authorization_refusal`, шесть копий делегируют; проверки
  `sub`/`sid`/`aud`/подписи/окна `exp` → `access_token.py`), S-15 ×2 (разделение действие/проверка
  для профиля; `Rotation` несёт `stored_after`/`session_ids_after`), тройной assert `refresh_token` снят.
- Оставлено: P-16 (прямое чтение строки в Statements) — решение координатора, ADR-дополнение.
- Прогон: targeted 13 passed / 1 skipped; полный acceptance 127 passed / 19 skipped.

## Refactor (детекторы M/D/T → refactor-agent)

- Итоги в отдельном коммите `refactor:`; Stage 1 закрыт до него (снимок дерева после test-review).
