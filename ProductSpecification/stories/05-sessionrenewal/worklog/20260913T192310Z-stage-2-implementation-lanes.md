# 2.1 Действующая сессия получает новую пару токенов — stage-2 implementation lanes

Started: 2026-09-13T19:23:10Z

Outcome: completed

- Context: план Stage 2 на чекбоксе записан для Python-бэкенда; после Task 2 (переписывание на
  Java 21, коммиты `2658336`..`60ef063`) скелет Stage 1 живёт в Java-модулях со stub-телами
  `throw new UnsupportedOperationException()`. Замороженные символы сохранены: порты,
  `RefreshSessionRequest`, `RotatedSessionTokens`, конструктор сервиса, `SessionEntity`
  (`auth.t_sessions`, changelog `0003-auth-sessions.xml`), `RestPaths.TOKEN_PREFIX`,
  `POST /refresh`, DTO `session{id,refreshToken,accessToken}`.
- Normalization: полоса `application` исключена — её дельта (`JwtAccessTokenIssuer`,
  `SecureRandomRefreshTokenGenerator`, `SystemClock`, `AuthTokenProperties`,
  `DomainPolicyConfiguration.sessionPolicy`, переменные `ACCESS_TOKEN_TTL_SECONDS`/
  `REFRESH_TOKEN_TTL_SECONDS`/`JWT_SECRET` в `.env.example` и `setup-ports.sh`) уже реализована
  портом Task 2; контроллер монтируется component-scan. Проверка маршрута — композиционная
  верификация Stage 3 (acceptance).
- Lanes: три непересекающиеся полосы — usecase, adapter-storage, adapter-rest.
- RED (all three predictions matched): rest `AuthTokenControllerTest` 2 tests → 500 вместо 200,
  сервис не вызван; storage `SessionRepositoryTest` 6 tests → `UnsupportedOperationException`
  в обоих методах порта; usecase `RefreshSessionRotatesTokensTest` 3 tests →
  `UnsupportedOperationException` в `RefreshSessionTokensService.refresh:33`.
- Test review: rest — `any()`+`ArgumentCaptor` заменены на `eq(EXPECTED_REQUEST)`;
  storage — кейс «уже ротированный токен» стал настоящим replay после первой ротации
  (проверяется нетронутая ротированная строка + count 1); usecase — `.as()` на всех
  ассертах, проверка `users` фейка в `assertNoNewSessionRowIsCreated`.
- GREEN join: rest `AuthTokenControllerTest` включён, модуль 25 passed / 0 skipped;
  storage — на join `findActiveByRefreshToken` падал с «LogicalConnection is closed»
  (`getResultStream` вне транзакции), координатор добавил `@Transactional` по идиоме
  `ActiveSessionRepository`; модуль 31 passed / 0 skipped; usecase — модуль 26 passed / 0 skipped.
- Combined: `:backend:architecture:test` 5 passed.
- Отказ в usecase — существующий `Unauthorized.of(AuthFailureReason.SESSION)` (единый 401
  по decision record), новых типов исключений нет.
- Commits: rest RED `af4fd9b`, GREEN `33f51f2`; storage RED `0fd0150`, GREEN `b5479bb`;
  usecase RED `a327105`, GREEN `d985d31`.
- Coverage (report-only, шагов не добавлено): rest — `SessionRefreshRequestDto:10` (не-строковый
  refreshToken) принадлежит Tier 2 сценарию 1.1, `toString`-редакция DTO — вне сценариев, отброшено;
  storage — `SessionRepository` 100% строк/веток, `SessionMapper.toRotatedEntity/toEntity` — мёртвые
  stub'ы Stage 1 → снос в refactor; usecase — `RefreshSessionTokensService:41` (нет активной сессии → 401)
  → Tier 2 3.1, `:45-46` (нулевой rowcount) → 3.3, `Session.isExpiredAt` без production-вызова → 3.2;
  граница истечения в production живёт в JPQL `expiresAt > :now`, доменный метод — её второе
  выражение для фейков.
- Refactor rest: детекторы M/D/T — A8 (тернар, borderline), A7b/A22 (`RotatedSessionDto` ≡
  `IssuedSessionDto`, замороженные поверхности Stage 1); вердикт refactor-agent NO ACTION по всем,
  коммита нет.
- Refactor storage+usecase: 12 находок M/D/T применены одним refactor-agent (A11 мёртвые stub'ы
  `SessionMapper`; B6 фейк вызывает `Session.isExpiredAt`; A51 `Session.rotatedTo`; A1/A32/A7
  `refresh()` → `requireActiveSession`/`persistRotation`/`sessionUnauthorized`; A22 фейк наследует
  `FakeSessionIssuance`, общий `ResultSetColumns.instantOf`, `AuthVerifyFixtures.SESSION_POLICY`;
  A31 `EmailCodeLogin` разгрузил Statements с 11 до 7 зависимостей; A27/A21/A7 в Statements).
  Верификация после refactor: usecase 26, storage 31, rest 25, architecture 5 — все passed.
  Коммит `4fa82fd`.

<!-- stage-2-plan:
usecase: unit=RefreshSessionTokensService.refresh; writes=[backend/domain/src/main/java/com/uwords/domain/auth/session/Session.java: bodies of isExpiredAt/rotate/accessTokenClaims, backend/usecase/src/main/java/com/uwords/usecase/service/auth/RefreshSessionTokensService.java: body of refresh() — RefreshToken.of, single now, find, mint+sign before write, conditional rotate, uniform unauthorized on zero rows, backend/usecase/src/test/java/com/uwords/usecase/service/auth/RefreshSessionRotatesTokensTest.java: scenario test on port fakes, backend/usecase/src/test/java/com/uwords/usecase/testing/fakes/FakeSessionRepository.java: SessionRepositoryPort fake with rotation journal, backend/usecase/src/test/java/com/uwords/usecase/testing/statements/RefreshSessionStatements.java: rotation Statements (+ fixtures under testing/ as needed)]; frozen-surfaces=[SessionRepositoryPort.findActiveByRefreshToken/rotateRefreshToken, RefreshTokenGeneratorPort.generate, AccessTokenIssuerPort.issue, ClockPort.now, RefreshSessionRequest, RotatedSessionTokens, RefreshSessionTokensService(ctor), SessionPolicy, RefreshToken, AccessTokenClaims]
adapter-storage: unit=SessionRepository/auth.t_sessions; writes=[backend/adapters/storage/src/main/java/com/uwords/adapter/storage/repository/SessionRepository.java: both port methods — parameterized JPQL, rowcount authoritative, backend/adapters/storage/src/main/java/com/uwords/adapter/storage/mapper/SessionMapper.java: bodies (unused stubs may be dropped by refactor), backend/adapters/storage/src/test/java/com/uwords/adapter/storage/SessionRepositoryTest.java: conditional rotation, zero rowcount, find active/expired/unknown, backend/adapters/storage/src/test/java/com/uwords/adapter/storage/testing/statements/SessionRepositoryStatements.java: session row Statements (+ testing/SessionRows/Data as needed)]; frozen-surfaces=[SessionEntity, changelog 0003-auth-sessions.xml, SessionRepositoryPort, Session, RefreshToken, StorageRepository, StorageTest]
adapter-rest: unit=AuthTokenController POST /api/v1/auth/token/refresh; writes=[backend/adapters/rest/src/main/java/com/uwords/adapter/rest/controller/AuthTokenController.java: handler body — delegate and map 200, backend/adapters/rest/src/main/java/com/uwords/adapter/rest/dto/auth/SessionRefreshRequestDto.java: toUsecaseRequest body, backend/adapters/rest/src/main/java/com/uwords/adapter/rest/dto/auth/SessionRefreshResponseDto.java: from body, backend/adapters/rest/src/test/java/com/uwords/adapter/rest/AuthTokenControllerTest.java: MockMvc over a Mockito-stubbed service, backend/adapters/rest/src/test/java/com/uwords/adapter/rest/testing/RefreshSessionStatements.java: refresh Statements (+ RefreshSessionData as needed)]; frozen-surfaces=[RestPaths.TOKEN_PREFIX, POST /refresh, SessionRefreshRequestDto(refreshToken), RotatedSessionDto{id,refreshToken,accessToken}, SessionRefreshResponseDto.session, RefreshSessionTokensService.refresh, RefreshSessionRequest, RotatedSessionTokens, GlobalExceptionHandler]
application: NO_DELTA (ported in Task 2)
-->
<!-- lanes: rest={red:af4fd9b,green:33f51f2,coverage:REPORTED,refactor:NO_CHANGE}; storage={red:0fd0150,green:b5479bb,coverage:REPORTED,refactor:4fa82fd}; usecase={red:a327105,green:d985d31,coverage:REPORTED,refactor:4fa82fd} -->
