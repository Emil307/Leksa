# Story 4: AccessTokenGuard — Progress

## Spec
- [x] interview
- [x] story
- [S] mockups (UI вне скоупа; desktop 0 = mobile 0)
- [x] api-spec
- [x] test-spec

## Tier 1 — Backend Scenarios (01_API_Tests.md)

### 1.1 Пользователь с действующей сессией получает всю свою запись
- [x] stage-1 acceptance RED + contract design
<!-- stage-1: acceptance=e849029,db8cfa0; design=8f12f0a -->
- [x] approve stage-1 contracts
- [x] stage-2 implementation lanes
<!-- stage-2-plan:
usecase: unit=request authentication + profile read behavior; writes=[backend/domain/src/domain/auth/session/bearer_credential.py: implement of() incl. octet limit/scheme/single-token, backend/domain/src/domain/auth/session/verified_access_token.py: implement of() per-claim validation + is_expired_at, backend/domain/src/domain/auth/session/active_session.py: implement authorizes(), backend/domain/src/domain/auth/user/gender.py: implement parse(), backend/usecase/src/usecase/services/auth/authenticate_request.py: implement authenticate() incl. UnavailableException->unauthorized(STORAGE), backend/usecase/src/usecase/services/profile/read_user_profile.py: implement read() incl. absent-account refusal, backend/usecase/tests/services/auth/test_authenticate_request.py: new focused scenario tests, backend/usecase/tests/services/profile/test_read_user_profile.py: new focused scenario tests, backend/usecase/tests/usecase_testing/fakes/access_token_decoder.py: new fake, backend/usecase/tests/usecase_testing/fakes/active_session_repository.py: new fake, backend/usecase/tests/usecase_testing/fakes/user_repository.py: new fake, backend/usecase/tests/usecase_testing/fakes/fixed_clock.py: new controllable clock, backend/usecase/tests/usecase_testing/statements/auth.py: new Statements]; frozen-surfaces=[AccessTokenDecoderPort.decode, ActiveSessionRepositoryPort.find_by_id, UserRepositoryPort.find_by_id, ClockPort.now, AuthenticatedCaller, AuthFailureReason, unauthorized(), User, API_AUDIENCE, MIN_EXPIRY_SECONDS, MAX_EXPIRY_SECONDS, MAX_AUTHORIZATION_HEADER_OCTETS]
adapter-storage: unit=PostgreSQL access to auth.t_sessions and auth.t_users; writes=[backend/adapters/storage/src/adapter_storage/repositories/active_session.py: implement find_by_id + UnavailableException translation, backend/adapters/storage/src/adapter_storage/repositories/user.py: implement find_by_id + UnavailableException translation, backend/adapters/storage/src/adapter_storage/mappers/active_session.py: implement to_domain incl. NULL expires_at -> None and naive->UTC, backend/adapters/storage/src/adapter_storage/mappers/user.py: implement to_domain incl. unknown-gender refusal, backend/adapters/storage/tests/test_active_session_repository.py: new focused tests, backend/adapters/storage/tests/test_user_repository.py: new focused tests, backend/adapters/storage/tests/test_auth_users_migration.py: new re-apply/idempotency test, backend/adapters/storage/tests/storage_testing/__init__.py: new support package, backend/adapters/storage/tests/storage_testing/auth_rows.py: new row fixtures]; frozen-surfaces=[ActiveSession, User, Gender, UserEntity column set, SessionEntity (read-only, owned by Story 5), revision id 0002_auth_users, ActiveSessionRepositoryPort.find_by_id, UserRepositoryPort.find_by_id]
adapter-rest: unit=HTTP boundary of the guarded profile endpoint; writes=[backend/adapters/rest/src/adapter_rest/security/access_token_guard.py: implement guard() reading the raw Authorization header without re-encoding, backend/adapters/rest/src/adapter_rest/routers/profile.py: implement read_profile handler, backend/adapters/rest/src/adapter_rest/schemas/profile.py: implement from_domain and both field serializers, backend/adapters/rest/tests/routers/test_profile_router.py: new focused tests, backend/adapters/rest/tests/test_exception_handlers.py: add uniform-401 body/log assertions, backend/adapters/rest/tests/rest_testing/profile.py: new Statements]; frozen-surfaces=[create_profile_router signature, create_access_token_guard signature, UserProfileResponse field+alias set, UNAUTHORIZED_BODY, PROFILE_PATH, AuthenticateRequestService.authenticate, ReadUserProfileService.read, AuthenticatedCaller]
adapter-application-security: unit=JWT verification adapter and composition root; writes=[backend/application/src/application/security/jwt_access_token_decoder.py: implement decode() with the HS256 allow-list and verify_exp/verify_aud off, backend/application/src/application/wiring.py: implement get_authenticate_request_service and get_read_user_profile_service, backend/application/src/application/main.py: include the profile router, backend/application/tests/test_app_factory.py: assert the profile route is mounted and boot fails on a blank secret, backend/application/tests/test_jwt_access_token_decoder.py: new focused tests, infrastructure/scripts/setup-ports.sh: emit JWT_SECRET, infrastructure/.env: regenerated with JWT_SECRET, backend/application/src/application/security/system_clock.py: implement now() — ownership unfrozen by user decision 2026-09-03, backend/application/tests/test_system_clock.py: focused tests for the real wired clock]; frozen-surfaces=[AccessTokenDecoderPort.decode, AccessTokenVerificationSettings.jwt_secret, ACCEPTED_ALGORITHMS, create_profile_router, AuthenticateRequestService.__init__, ReadUserProfileService.__init__, ]
-->
<!-- stage-2: lanes=a151454; adapter-application-security reopened=98468d9,7a1cbfd; log=worklog/20260903T074500Z-stage-2-reopened-system-clock.md -->
- [x] stage-3 acceptance GREEN + review
<!-- stage-3: acceptance=b2a55b4; agent-review=BLOCK; premortem=CONCERNS; log=worklog/20260903T081500Z-stage-3-acceptance-green-review.md -->
- [x] resolve stage-3 cycle proposals
<!-- stage-3-consent: accepted=P2 openapi-contract -> Tier 2 Backend 4.1; declined=P1 db-timeout-500 -->

## Harvest — Tier 1 → Tier 2

- [x] harvest
<!-- harvest: set=18; green=11; red=2; not-black-box=5; baseline=688d65d; earned=71/71 -->

## Tier 2 — Backend Scenarios (01_API_Tests.md)

### 1.2 Nullable-поля, Unicode и даты возвращаются без подмены
- [x] stage-1 acceptance RED + contract design
<!-- harvest: acceptance=tests/backend/profile/test_profile_field_fidelity_acceptance.py; green=3; baseline=RED 3/3 -> earned -->
- [S] approve stage-1 contracts (harvest: контракт Tier 1 не меняется)
- [S] stage-2 implementation lanes (harvest: реализует сериализаторы schemas/profile.py и mappers/user.py из Tier 1)
- [S] stage-3 acceptance GREEN + review (harvest: тест зелёный как есть, baseline earned)

### 2.1 Запрос профиля с невалидной авторизацией отклоняется единообразно
- [x] stage-1 acceptance RED + contract design
<!-- harvest: acceptance=tests/backend/profile/test_profile_auth_refusal_acceptance.py; green=18; baseline=RED 18/18 -> earned -->
- [S] approve stage-1 contracts (harvest: контракт Tier 1 не меняется)
- [S] stage-2 implementation lanes (harvest: реализует access_token_guard.py и единый 401 в AuthenticateRequestService из Tier 1)
- [S] stage-3 acceptance GREEN + review (harvest: тест зелёный как есть, baseline earned)

### 3.1 Клиентское значение userId не может выбрать чужой профиль
- [x] stage-1 acceptance RED + contract design
<!-- harvest: acceptance=tests/backend/profile/test_profile_owner_selection_acceptance.py; green=1; baseline=RED 1/1 -> earned -->
- [S] approve stage-1 contracts (harvest: контракт Tier 1 не меняется)
- [S] stage-2 implementation lanes (harvest: реализует routers/profile.py читает только AuthenticatedCaller из Tier 1)
- [S] stage-3 acceptance GREEN + review (harvest: тест зелёный как есть, baseline earned)

### 4.1 Опубликованный контракт описывает чтение профиля как защищённое
<!-- review-origin: boundary -->
<!-- harvest: acceptance=tests/backend/contract/test_profile_contract_document_acceptance.py; red=1 (маркер отключения на месте) -->
- [x] stage-1 acceptance RED + contract design
- [~] approve stage-1 contracts (log: worklog/20260903T101500Z-stage-1-contract-document.md)
- [ ] stage-2 implementation lanes
- [ ] stage-3 acceptance GREEN + review

## Tier 2 — Security Scenarios (05_Security_Tests.md)

### 1.1 Лимит Authorization считается по wire bytes до разбора JWT
- [x] stage-1 acceptance RED + contract design
<!-- harvest: acceptance=tests/backend/security/test_authorization_header_limit_acceptance.py; green=3; baseline=RED 3/3 -> earned -->
- [S] approve stage-1 contracts (harvest: контракт Tier 1 не меняется)
- [S] stage-2 implementation lanes (harvest: реализует BearerCredential.of с лимитом октетов до разбора JWT из Tier 1)
- [S] stage-3 acceptance GREEN + review (harvest: тест зелёный как есть, baseline earned)

### 2.1 Сервер принимает только доверенный HS256 JWT
- [x] stage-1 acceptance RED + contract design
<!-- harvest: acceptance=tests/backend/security/test_jwt_trust_acceptance.py; green=5; baseline=RED 5/5 -> earned -->
- [S] approve stage-1 contracts (harvest: контракт Tier 1 не меняется)
- [S] stage-2 implementation lanes (harvest: реализует JwtAccessTokenDecoder с allow-list HS256 из Tier 1)
- [S] stage-3 acceptance GREEN + review (harvest: тест зелёный как есть, baseline earned)

### 2.2 Каждый обязательный claim проверяется без неявных преобразований
- [x] stage-1 acceptance RED + contract design
<!-- harvest: acceptance=tests/backend/security/test_jwt_claims_acceptance.py; green=23; baseline=RED 23/23 -> earned -->
- [S] approve stage-1 contracts (harvest: контракт Tier 1 не меняется)
- [S] stage-2 implementation lanes (harvest: реализует VerifiedAccessToken.of с проверкой каждого claim из Tier 1)
- [S] stage-3 acceptance GREEN + review (harvest: тест зелёный как есть, baseline earned)

### 2.3 Обе границы истечения используют одни управляемые часы
- [x] stage-1 acceptance RED + contract design
<!-- harvest: acceptance=tests/backend/security/test_expiry_clock_acceptance.py; green=10; baseline=RED 10/10 -> earned -->
- [S] approve stage-1 contracts (harvest: контракт Tier 1 не меняется)
- [S] stage-2 implementation lanes (harvest: реализует is_expired_at и ActiveSession.authorizes на одном ClockPort из Tier 1)
- [S] stage-3 acceptance GREEN + review (harvest: тест зелёный как есть, baseline earned)

### 2.4 Решение о сессии перечитывается на каждом запросе и каждом инстансе
- [x] stage-1 acceptance RED + contract design
<!-- harvest: acceptance=tests/backend/security/test_session_recheck_acceptance.py; green=1; baseline=RED 1/1 -> earned -->
- [S] approve stage-1 contracts (harvest: контракт Tier 1 не меняется)
- [S] stage-2 implementation lanes (harvest: реализует ActiveSessionRepository.find_by_id на каждом запросе из Tier 1)
- [S] stage-3 acceptance GREEN + review (harvest: тест зелёный как есть, baseline earned)

### 3.1 Запрос профиля возвращает безопасно сериализованные данные владельца токена
- [x] stage-1 acceptance RED + contract design
<!-- harvest: acceptance=tests/backend/security/test_profile_serialization_acceptance.py; green=1; baseline=RED 1/1 -> earned -->
- [S] approve stage-1 contracts (harvest: контракт Tier 1 не меняется)
- [S] stage-2 implementation lanes (harvest: реализует UserProfileResponse.from_domain из Tier 1)
- [S] stage-3 acceptance GREEN + review (harvest: тест зелёный как есть, baseline earned)

### 4.1 Каждый auth-отказ диагностируется безопасно и закрывает доступ к профилю
- [x] stage-1 acceptance RED + contract design
<!-- harvest: acceptance=tests/backend/security/test_auth_failure_diagnostics_acceptance.py; green=5; baseline=RED 5/5 -> earned -->
- [S] approve stage-1 contracts (harvest: контракт Tier 1 не меняется)
- [S] stage-2 implementation lanes (harvest: реализует unauthorized(AuthFailureReason) и UNAUTHORIZED_BODY из Tier 1)
- [S] stage-3 acceptance GREEN + review (harvest: тест зелёный как есть, baseline earned)

### 4.2 Успешный запрос не создаёт сигнал auth-отказа
- [S] stage-1 acceptance RED + contract design (harvest: отсутствие сигнала отказа видно только в логах; место — rest/tests/test_exception_handlers.py)
- [S] approve stage-1 contracts (harvest: отсутствие сигнала отказа видно только в логах; место — rest/tests/test_exception_handlers.py)
- [S] stage-2 implementation lanes (harvest: отсутствие сигнала отказа видно только в логах; место — rest/tests/test_exception_handlers.py)
- [S] stage-3 acceptance GREEN + review (harvest: отсутствие сигнала отказа видно только в логах; место — rest/tests/test_exception_handlers.py)

### 4.3 Отсутствующий или пустой секрет подписи ломает старт
<!-- harvest: acceptance=tests/backend/security/test_signing_secret_boot_acceptance.py; green=2; red=1 (пробельный секрет, маркер отключения) -->
- [ ] stage-1 acceptance RED + contract design
- [ ] approve stage-1 contracts
- [ ] stage-2 implementation lanes
- [ ] stage-3 acceptance GREEN + review

## Tier 2 — Infrastructure Scenarios (04_Infrastructure_Tests.md)

### 1.1 Срок сессии вводится без разрыва смешанного развёртывания
- [S] stage-1 acceptance RED + contract design (harvest: additive-раскатка отложена decisions/auth-schema-ownership-decision.md; expires_at уже NOT NULL в 0001)
- [S] approve stage-1 contracts (harvest: additive-раскатка отложена decisions/auth-schema-ownership-decision.md; expires_at уже NOT NULL в 0001)
- [S] stage-2 implementation lanes (harvest: additive-раскатка отложена decisions/auth-schema-ownership-decision.md; expires_at уже NOT NULL в 0001)
- [S] stage-3 acceptance GREEN + review (harvest: additive-раскатка отложена decisions/auth-schema-ownership-decision.md; expires_at уже NOT NULL в 0001)

### 1.2 Повтор завершённого rollout не меняет достигнутое состояние
- [S] stage-1 acceptance RED + contract design (harvest: идемпотентность повтора закрыта storage/tests/test_auth_users_migration.py)
- [S] approve stage-1 contracts (harvest: идемпотентность повтора закрыта storage/tests/test_auth_users_migration.py)
- [S] stage-2 implementation lanes (harvest: идемпотентность повтора закрыта storage/tests/test_auth_users_migration.py)
- [S] stage-3 acceptance GREEN + review (harvest: идемпотентность повтора закрыта storage/tests/test_auth_users_migration.py)

### 1.3 Сбой backfill откатывается целиком и безопасно повторяется
- [S] stage-1 acceptance RED + contract design (harvest: backfill-ревизии не существует — раскатка отложена тем же решением)
- [S] approve stage-1 contracts (harvest: backfill-ревизии не существует — раскатка отложена тем же решением)
- [S] stage-2 implementation lanes (harvest: backfill-ревизии не существует — раскатка отложена тем же решением)
- [S] stage-3 acceptance GREEN + review (harvest: backfill-ревизии не существует — раскатка отложена тем же решением)

### 2.1 Проверка сессии освобождает соединение на каждом исходе
- [x] stage-1 acceptance RED + contract design
<!-- harvest: acceptance=tests/backend/infrastructure/test_connection_release_acceptance.py; green=1; baseline=RED 1/1 -> earned -->
- [S] approve stage-1 contracts (harvest: контракт Tier 1 не меняется)
- [S] stage-2 implementation lanes (harvest: реализует область сессии в репозиториях auth из Tier 1)
- [S] stage-3 acceptance GREEN + review (harvest: тест зелёный как есть, baseline earned)

### 2.2 После восстановления PostgreSQL корректный запрос снова проходит
- [S] stage-1 acceptance RED + contract design (harvest: требует остановки общего PostgreSQL — запрещено .claude/rules/infrastructure.md)
- [S] approve stage-1 contracts (harvest: требует остановки общего PostgreSQL — запрещено .claude/rules/infrastructure.md)
- [S] stage-2 implementation lanes (harvest: требует остановки общего PostgreSQL — запрещено .claude/rules/infrastructure.md)
- [S] stage-3 acceptance GREEN + review (harvest: требует остановки общего PostgreSQL — запрещено .claude/rules/infrastructure.md)
