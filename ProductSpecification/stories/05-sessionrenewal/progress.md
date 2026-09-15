# Story 5: SessionRenewal — Progress

## Spec
- [x] interview
- [x] story
- [S] mockups (server-only API story — no screen states)
- [x] api-spec
- [x] test-spec

## Tier 1 — Backend Scenarios (01_API_Tests.md)

### 2.1 Действующая сессия получает новую пару токенов
- [x] stage-1 acceptance RED + contract design
<!-- stage-1: acceptance=688d65d,9d8ab7e; design=44ad11f -->
- [x] approve stage-1 contracts
- [x] stage-2 implementation lanes (reopened: usecase + application — unique access-token claim; worklog: 20260914T102200Z-stage-2-implementation-lanes-reopened.md)
<!-- stage-2-plan:
usecase: unit=RefreshSessionTokensService; writes=[backend/usecase/src/usecase/services/auth/refresh_session.py: implement refresh() — validation, single now, mint+sign before write, conditional write, single 401, backend/usecase/tests/services/auth/test_refresh_session_tokens.py: focused scenario tests on port fakes, backend/usecase/tests/usecase_testing/fakes/session_repository.py: SessionRepositoryPort fake with changed-row counter, backend/usecase/tests/usecase_testing/fakes/tokens.py: fakes for RefreshTokenGeneratorPort/AccessTokenIssuerPort/ClockPort, backend/usecase/tests/usecase_testing/statements/session.py: rotation Statements, backend/domain/src/domain/auth/session/refresh_token.py: bodies of of()/matches(), backend/domain/src/domain/auth/session/session_policy.py: bodies of of()/expiry/truncate(), backend/domain/src/domain/auth/session/session.py: bodies of is_expired_at()/rotate()/access_token_claims(), backend/domain/src/domain/auth/session/access_token_claims.py: body of numeric_date()]; frozen-surfaces=[SessionRepositoryPort.find_active_by_refresh_token, SessionRepositoryPort.rotate_refresh_token, RefreshTokenGeneratorPort.generate, AccessTokenIssuerPort.issue, ClockPort.now, RefreshSessionRequest, RotatedSessionTokens, RefreshSessionTokensService.__init__]
adapter-storage: unit=SessionRepository/auth.t_sessions; writes=[backend/adapters/storage/src/adapter_storage/repositories/session.py: implement both methods with parameterized statements, rowcount authoritative, backend/adapters/storage/src/adapter_storage/mappers/session.py: bodies of to_domain/build_rotation_dict/build_create_dict, backend/adapters/storage/tests/repositories/test_session_repository.py: focused tests for conditional rotation and zero rowcount, backend/adapters/storage/tests/test_auth_sessions_migration.py: alembic upgrade head — exactly one head, table and unique index present, backend/adapters/storage/tests/storage_testing/__init__.py: package init, backend/adapters/storage/tests/storage_testing/sessions.py: session row fixtures]; frozen-surfaces=[SessionEntity (table name, auth schema, column set, ix_t_sessions_user_id, uq_t_sessions_refresh_token), revision 0001_auth_sessions and its id, SessionRepositoryPort (both signatures), Session, RefreshToken]
adapter-rest: unit=create_auth_token_router; writes=[backend/adapters/rest/src/adapter_rest/routers/auth_token.py: handler body — delegate to service and map response, backend/adapters/rest/src/adapter_rest/schemas/session.py: bodies of to_usecase()/from_usecase() with allowlist rejection, backend/adapters/rest/tests/routers/test_auth_token_router.py: focused tests over ASGITransport with a stub service, backend/adapters/rest/tests/rest_testing/session.py: refresh Statements/stubs]; frozen-surfaces=[TOKEN_PREFIX, route POST /refresh, SessionRefreshRequest.refreshToken, RotatedSessionSchema{id,refreshToken,accessToken}, SessionRefreshResponse.session, RefreshSessionTokensService.refresh, RefreshSessionRequest, RotatedSessionTokens]
application: unit=composition root; writes=[backend/application/src/application/security/jwt_access_token_issuer.py: body of issue() on the HS256 constant, backend/application/src/application/security/refresh_token_generator.py: body of generate(), backend/application/src/application/security/system_clock.py: body of now(), backend/application/src/application/wiring.py: body of get_refresh_session_service(), backend/application/src/application/settings.py: include AuthTokenSettings in Settings, backend/application/src/application/main.py: mount create_auth_token_router, backend/application/tests/test_refresh_session_wiring.py: route mounted and service assembled, backend/application/tests/test_app_factory.py: extend for the new route, infrastructure/.env.example: declare ACCESS_TOKEN_TTL_SECONDS/REFRESH_TOKEN_TTL_SECONDS/JWT_SECRET, infrastructure/scripts/setup-ports.sh: generate the same three variables into infrastructure/.env]; frozen-surfaces=[AccessTokenIssuerPort.issue, RefreshTokenGeneratorPort.generate, ClockPort.now, SessionPolicy.of, create_auth_token_router, RefreshSessionTokensService.__init__, AuthTokenSettings (field names and aliases), ALGORITHM]
-->
- [x] stage-3 acceptance GREEN + review

## Tier 1 — Integration Scenarios (06_Integration_Tests.md)

### 1.1 Успешный запрос согласованно обновляет хранилище и выпускает JWT
- [x] stage-1 acceptance RED + contract design
- [x] approve stage-1 contracts
- [S] stage-2 implementation lanes (ALREADY_GREEN + NO_DELTA; worklog 20260914T110500Z)
- [x] stage-3 acceptance GREEN + review

## Harvest — Tier 1 → Tier 2

- [x] harvest

## Tier 2 — Backend Scenarios (01_API_Tests.md)

### 1.1 Недопустимый запрос обновления отклоняется без изменения сессии
- [x] stage-1 acceptance RED + contract design
- [S] approve stage-1 contracts (harvest ALREADY_GREEN, earned at baseline b4e9f8e)
- [S] stage-2 implementation lanes (реализует: GlobalExceptionHandler.handleUnreadableRequest/handleDomainException + RefreshToken.of)
- [S] stage-3 acceptance GREEN + review (тест включён и зелёный; worklog 20260914T114500Z)

### 1.3 ASCII-токен предельной длины проходит валидацию
- [x] stage-1 acceptance RED + contract design
- [S] approve stage-1 contracts (harvest ALREADY_GREEN, earned at baseline b4e9f8e)
- [S] stage-2 implementation lanes (реализует: RefreshToken.of MAX_TOKEN_BYTES=512 + RefreshSessionTokensService.refresh)
- [S] stage-3 acceptance GREEN + review (тест включён и зелёный; worklog 20260914T114500Z)

### 2.2 Новая пара сохраняет владельца и получает точные сроки
- [x] stage-1 acceptance RED + contract design
- [S] approve stage-1 contracts (harvest ALREADY_GREEN, earned at baseline b4e9f8e)
- [S] stage-2 implementation lanes (реализует: RefreshSessionTokensService.refresh + SessionPolicy.refreshExpiryAt/accessExpiryAt + JwtAccessTokenIssuer)
- [S] stage-3 acceptance GREEN + review (тест включён и зелёный; worklog 20260914T114500Z)

### 2.3 Ротация не затрагивает соседние сессии
- [x] stage-1 acceptance RED + contract design
- [S] approve stage-1 contracts (harvest ALREADY_GREEN, earned at baseline b4e9f8e)
- [S] stage-2 implementation lanes (реализует: SessionRepository.rotateRefreshToken (ROTATE_SESSION_UPDATE по id+token))
- [S] stage-3 acceptance GREEN + review (тест включён и зелёный; worklog 20260914T114500Z)

### 3.1 Недействительные refresh-токены неразличимы снаружи
- [x] stage-1 acceptance RED + contract design
- [S] approve stage-1 contracts (harvest ALREADY_GREEN, earned at baseline b4e9f8e)
- [S] stage-2 implementation lanes (реализует: RefreshSessionTokensService.sessionUnauthorized + GlobalExceptionHandler.handleUnauthorized)
- [S] stage-3 acceptance GREEN + review (тест включён и зелёный; worklog 20260914T114500Z)

### 3.2 Срок сессии имеет строгую границу истечения
- [x] stage-1 acceptance RED + contract design
- [S] approve stage-1 contracts (harvest ALREADY_GREEN, earned at baseline b4e9f8e)
- [S] stage-2 implementation lanes (реализует: SessionRepository ACTIVE_SESSION_QUERY/ROTATE_SESSION_UPDATE (expiresAt > :now))
- [S] stage-3 acceptance GREEN + review (тест включён и зелёный; worklog 20260914T114500Z)

### 3.3 Один refresh-токен выигрывает только одну конкурентную ротацию
- [x] stage-1 acceptance RED + contract design
- [S] approve stage-1 contracts (harvest ALREADY_GREEN, earned at baseline b4e9f8e)
- [S] stage-2 implementation lanes (реализует: SessionRepository.rotateRefreshToken rowcount + RefreshSessionTokensService.persistRotation)
- [S] stage-3 acceptance GREEN + review (тест включён и зелёный; worklog 20260914T114500Z)

## Tier 2 — Integration Scenarios (06_Integration_Tests.md)

### 1.2 Условная запись разрешает только одного конкурентного победителя
- [x] stage-1 acceptance RED + contract design
- [S] approve stage-1 contracts (harvest ALREADY_GREEN, earned at baseline b4e9f8e)
- [S] stage-2 implementation lanes (реализует: SessionRepository.rotateRefreshToken (условный UPDATE, rowcount==1))
- [S] stage-3 acceptance GREEN + review (тест включён и зелёный; worklog 20260914T114500Z)

### 1.3 Потерянный успешный ответ не допускает второй ротации
- [x] stage-1 acceptance RED + contract design
- [S] approve stage-1 contracts (harvest ALREADY_GREEN, earned at baseline b4e9f8e)
- [S] stage-2 implementation lanes (реализует: SessionRepository.rotateRefreshToken + RefreshSessionTokensService.persistRotation)
- [S] stage-3 acceptance GREEN + review (тест включён и зелёный; worklog 20260914T114500Z)

## Tier 2 — Security Scenarios (05_Security_Tests.md)

### 1.1 Недопустимый запрос ротации обрабатывается на границе запроса
- [~] stage-1 acceptance RED + contract design (harvest RED: тест уже написан, 6 кейсов отключены)
- [ ] approve stage-1 contracts
- [ ] stage-2 implementation lanes
- [ ] stage-3 acceptance GREEN + review

### 1.3 SQL-метасимволы обрабатываются как обычный неизвестный токен
- [x] stage-1 acceptance RED + contract design
- [S] approve stage-1 contracts (harvest ALREADY_GREEN, earned at baseline b4e9f8e)
- [S] stage-2 implementation lanes (реализует: SessionRepository bound-параметры JPQL + RefreshToken.of + Unauthorized.of(SESSION))
- [S] stage-3 acceptance GREEN + review (тест включён и зелёный; worklog 20260914T114500Z)

### 2.1 Refresh-токен изменяет только принадлежащую ему сессию
- [ ] stage-1 acceptance RED + contract design (harvest RED: тест уже написан, 1 кейс отключён; worklog 20260914T114500Z)
- [ ] approve stage-1 contracts
- [ ] stage-2 implementation lanes
- [ ] stage-3 acceptance GREEN + review

### 2.2 Недоступная и отсутствующая сессии неразличимы снаружи
- [x] stage-1 acceptance RED + contract design
- [S] approve stage-1 contracts (harvest ALREADY_GREEN, earned at baseline b4e9f8e)
- [S] stage-2 implementation lanes (реализует: SessionRepository.findActiveByRefreshToken + RefreshSessionTokensService.requireActiveSession)
- [S] stage-3 acceptance GREEN + review (тест включён и зелёный; worklog 20260914T114500Z)

### 3.1 Новый access-токен имеет только разрешённый алгоритм и claims
- [x] stage-1 acceptance RED + contract design
- [S] approve stage-1 contracts (harvest ALREADY_GREEN, earned at baseline b4e9f8e)
- [S] stage-2 implementation lanes (реализует: JwtAccessTokenIssuer.issue (HS256, sub/sid/jti/exp/aud))
- [S] stage-3 acceptance GREEN + review (тест включён и зелёный; worklog 20260914T114500Z)

### 3.2 Ответы и журналы не раскрывают токены и внутренние детали
- [ ] stage-1 acceptance RED + contract design (harvest RED: тест уже написан, 1 кейс отключён; worklog 20260914T114500Z)
- [ ] approve stage-1 contracts
- [ ] stage-2 implementation lanes
- [ ] stage-3 acceptance GREEN + review

## Tier 2 — Infrastructure Scenarios (04_Infrastructure_Tests.md)

### 1.1 Отказ хранилища откатывает ротацию целиком
- [ ] stage-1 acceptance RED + contract design (harvest RED: тест уже написан, 1 кейс отключён; worklog 20260914T114500Z)
- [ ] approve stage-1 contracts
- [ ] stage-2 implementation lanes
- [ ] stage-3 acceptance GREEN + review

### 1.2 Ошибка выпуска токена не начинает ротацию
- [ ] stage-1 acceptance RED + contract design (harvest: INFEASIBLE_AT_ACCEPTANCE — RED только на usecase/adapter; worklog 20260914T114500Z)
- [ ] approve stage-1 contracts
- [ ] stage-2 implementation lanes
- [ ] stage-3 acceptance GREEN + review

### 1.3 Отказы ротации имеют безопасные операционные сигналы
- [ ] stage-1 acceptance RED + contract design (harvest: INFEASIBLE_AT_ACCEPTANCE — RED только на usecase/adapter; worklog 20260914T114500Z)
- [ ] approve stage-1 contracts
- [ ] stage-2 implementation lanes
- [ ] stage-3 acceptance GREEN + review

### 2.1 Некорректная конфигурация токенов запрещает запуск приложения
- [ ] stage-1 acceptance RED + contract design (harvest RED: тест уже написан, 2 кейса отключены; worklog 20260914T114500Z)
- [ ] approve stage-1 contracts
- [ ] stage-2 implementation lanes
- [ ] stage-3 acceptance GREEN + review

### 2.2 Соединение хранилища освобождается на каждом исходе
- [x] stage-1 acceptance RED + contract design
- [S] approve stage-1 contracts (harvest ALREADY_GREEN, earned at baseline b4e9f8e)
- [S] stage-2 implementation lanes (реализует: RefreshSessionTokensService.refresh (транзакция без исключений) + StorageDataSourceConfiguration Hikari)
- [S] stage-3 acceptance GREEN + review (тест включён и зелёный; worklog 20260914T114500Z)

### 2.3 Дробная доля времени не меняет единицы TTL
- [x] stage-1 acceptance RED + contract design
- [S] approve stage-1 contracts (review-fix: красный кейс переписан под ADR SessionPolicy.truncate, зелёный)
- [S] stage-2 implementation lanes (реализует: SessionPolicy.truncate + RefreshSessionTokensService.refresh)
- [S] stage-3 acceptance GREEN + review (тест включён и зелёный; worklog 20260914T114500Z)
