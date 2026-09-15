# Story 1: EmailCodeLogin — Progress

## Spec
- [x] interview
- [x] story
- [S] mockups (API-only repo — no frontend profile, per ProductSpecification/technology.md)
- [x] api-spec
- [x] test-spec

## Tier 1 — Backend Scenarios (01_API_Tests.md)

### 2.1 Запрос кода возвращает challenge и кладёт в очередь готовую заявку
- [x] stage-1 acceptance RED + contract design
<!-- stage-1: acceptance=28ffacd PASS (RED confirmed, marker added); design=9235fc1 PASS (35 files, ADR challenge-start-contracts-decision.md) -->
- [x] approve stage-1 contracts
- [x] stage-2 implementation lanes
<!-- stage-2-prerequisite (coordinator applies at approval, before dispatch — unassigned on purpose, so no lane depends on another):
requirements.txt: add `-e backend/adapters/cache`
.importlinter: add `adapter_cache` to root_packages and to the adapter layer line
pyproject.toml (root): add `backend/adapters/cache/tests` to pythonpath
-->
<!-- stage-2-plan:
usecase: unit=start-challenge use-case behaviour incl. the domain it delegates to; writes=[backend/domain/src/domain/auth/user/email.py: implement of/octet_length/masked, backend/domain/src/domain/auth/code/verification_code.py: implement of/matches, backend/domain/src/domain/auth/challenge/challenge_type.py: implement parse, backend/domain/src/domain/auth/challenge/challenge.py: implement create, backend/domain/src/domain/auth/email_code/strategy.py: implement subject_of/issue_secret/notification_for, backend/domain/src/domain/auth/challenge/strategy_registry.py: implement for_type, backend/usecase/src/usecase/services/auth/start_challenge.py: implement start, backend/usecase/tests/services/auth/test_start_challenge_queues_request.py: new focused test, backend/usecase/tests/usecase_testing/fakes/{challenge_store,notification_queue,clock,id_generator}.py: new port fakes, backend/usecase/tests/usecase_testing/fakes/code_generator.py: new CodeGenerator stub, backend/usecase/tests/usecase_testing/statements/auth.py: new Statements]; frozen-surfaces=[ChallengeStorePort.{acquire_cooldown,swap_challenge,discard_started_challenge}, CooldownAcquisition, NotificationQueuePort.enqueue, ClockPort.now, IdGeneratorPort.new_id, CodeGenerator.generate, StartChallengeRequest, StartedChallenge, ChallengeStrategy ABC, ChallengeSecret ABC, Challenge field set + ttl_seconds, OutboundNotification, OutboundEmail.payload(), ChallengeSubject, ChallengePolicy, CodePolicy]
adapter-cache: unit=Redis challenge-store boundary; writes=[backend/adapters/cache/src/adapter_cache/client.py: implement pooled client + close_redis, backend/adapters/cache/src/adapter_cache/challenge_store.py: implement the three port methods, backend/adapters/cache/src/adapter_cache/scripts.py: new Lua sources, backend/adapters/cache/tests/test_redis_challenge_store.py: new focused test, backend/adapters/cache/tests/cache_testing/{__init__.py,statements/challenge_store.py}: new support package]; frozen-surfaces=[ChallengeStorePort signatures, CooldownAcquisition, Challenge fields + ttl_seconds, RECORD_KEY/POINTER_KEY/COOLDOWN_KEY templates]
adapter-storage: unit=Postgres outbox boundary; writes=[backend/adapters/storage/src/adapter_storage/outbox_queue.py: implement enqueue, backend/adapters/storage/src/adapter_storage/repositories/notification_outbox.py: in-boundary collaborator — extend only if enqueue needs a custom query, backend/adapters/storage/src/adapter_storage/migrations/versions/<rev>_notifications_outbox.py: new migration creating schema notifications + t_outbox, backend/adapters/storage/tests/test_outbox_notification_queue.py: new focused test, backend/adapters/storage/tests/storage_testing/{__init__.py,statements/outbox.py}: new support package]; frozen-surfaces=[NotificationQueuePort.enqueue, OutboundEmail.payload()/notification_type, NotificationOutboxEntity columns, OutboxStatus]
adapter-rest: unit=HTTP boundary; writes=[backend/adapters/rest/src/adapter_rest/routers/auth.py: implement the handler body, backend/adapters/rest/tests/routers/test_auth_challenge_router.py: new focused test over ASGITransport with a fake service, backend/adapters/rest/tests/rest_testing/auth.py: new Statements/fake]; frozen-surfaces=[ChallengeStartRequest/ChallengeStartResponse field names + to_usecase/from_usecase, create_auth_challenge_router signature, CHALLENGE_PREFIX, StartAuthChallengeService.start signature]
application: unit=composition root; writes=[backend/application/src/application/system.py: new SystemClock/SecureNumericCodeGenerator/UuidGenerator, backend/application/src/application/settings.py: add ChallengeSettings + mail-template settings, backend/application/src/application/wiring.py: build template/strategy/registry/store/queue/service, backend/application/src/application/main.py: mount the router + close Redis in lifespan, backend/application/tests/test_app_factory.py: assert the start route is exposed]; frozen-surfaces=[the five port protocols it implements against, StartAuthChallengeService.__init__, create_auth_challenge_router, RedisChallengeStore/OutboxNotificationQueue constructors, ChallengePolicy + EmailCodeTemplate field sets]
-->
- [x] stage-3 acceptance GREEN + review
- [x] resolve stage-3 cycle proposals (worklog: 20260903T030000Z-stage-3-acceptance-green-review.md)

### 4.1 Существующий пользователь получает сессию по верному коду
- [x] stage-1 acceptance RED + contract design (worklog: 20260903T050000Z-stage-1-acceptance-red-contract-design.md)
- [x] approve stage-1 contracts
- [x] stage-2 implementation lanes (worklog: 20260903T060000Z-stage-2-implementation-lanes.md)
- [x] stage-3 acceptance GREEN + review (worklog: 20260903T070000Z-stage-3-acceptance-green-review.md)
- [x] resolve stage-3 cycle proposals (worklog: 20260903T070000Z-stage-3-acceptance-green-review.md)

### 4.2 Неизвестный email регистрируется при верном коде и получает сессию
- [x] stage-1 acceptance RED + contract design (worklog: 20260907T104500Z-stage-1-acceptance-red-contract-design.md)
- [x] approve stage-1 contracts (worklog: 20260907T110000Z-approve-stage-1-contracts.md)
- [S] stage-2 implementation lanes — ALREADY_GREEN, shipped by 4.1 stage 2 (worklog: 20260907T104500Z-stage-1-acceptance-red-contract-design.md)
- [x] stage-3 acceptance GREEN + review (worklog: 20260907T113000Z-stage-3-acceptance-green-review.md)

### 4.6 Пользователь, чей email записан в базе в другом регистре, не получает второго аккаунта
<!-- review-origin: boundary -->
- [x] stage-1 acceptance RED + contract design (worklog: 20260907T112000Z-stage-1-acceptance-red-contract-design.md)
- [x] approve stage-1 contracts (worklog: 20260907T120000Z-approve-stage-1-contracts.md)
- [x] stage-2 implementation lanes (worklog: 20260907T124500Z-stage-2-implementation-lanes.md)
- [x] stage-3 acceptance GREEN + review (worklog: 20260907T133000Z-stage-3-acceptance-green-review.md)

## Harvest — Tier 1 → Tier 2

- [x] harvest

## Tier 2 — Backend Scenarios (01_API_Tests.md)

### 1.1 Некорректное тело запроса кода отклоняется до постановки заявки в очередь
- [x] stage-1 acceptance RED + contract design — harvest: зелено как есть, реализовано в ChallengeType.parse + Email.of + ChallengeStartRequest.to_usecase
- [S] approve stage-1 contracts — harvest
- [S] stage-2 implementation lanes — harvest
- [S] stage-3 acceptance GREEN + review — harvest

### 2.4 Повторный запрос внутри кулдауна отклоняется и второй заявки не создаёт
- [x] stage-1 acceptance RED + contract design — harvest: зелено как есть, реализовано в StartAuthChallengeService._guard_cooldown + Lua ACQUIRE_COOLDOWN
- [S] approve stage-1 contracts — harvest
- [S] stage-2 implementation lanes — harvest
- [S] stage-3 acceptance GREEN + review — harvest

### 2.5 Повторный запрос после кулдауна выдаёт новый challenge и обесценивает прежний код
<!-- review-origin: boundary -->
- [~] stage-1 acceptance RED + contract design
- [ ] approve stage-1 contracts
- [ ] stage-2 implementation lanes
- [ ] stage-3 acceptance GREEN + review

### 3.1 Некорректный ввод на проверке кода отклоняется
- [x] stage-1 acceptance RED + contract design — harvest: зелено как есть, реализовано в ChallengeVerifyRequest + ChallengeId.of/PresentedSecret.of/VerificationCode.of
- [S] approve stage-1 contracts — harvest
- [S] stage-2 implementation lanes — harvest
- [S] stage-3 acceptance GREEN + review — harvest

### 4.3 Код с ведущим нулём проходит весь путь
- [x] stage-1 acceptance RED + contract design — harvest: зелено как есть, реализовано в SecureNumericCodeGenerator.generate + RedisChallengeStore._record_of
- [S] approve stage-1 contracts — harvest
- [S] stage-2 implementation lanes — harvest
- [S] stage-3 acceptance GREEN + review — harvest

### 4.5 Повторный вход по коду даёт новую сессию тому же пользователю
- [x] stage-1 acceptance RED + contract design — harvest: зелено как есть, реализовано в session_issuance._link_user + VerifyAuthChallengeService._issue_session
- [S] approve stage-1 contracts — harvest
- [S] stage-2 implementation lanes — harvest
- [S] stage-3 acceptance GREEN + review — harvest

### 5.1 Неверный код отклоняется и тратит попытку
- [x] stage-1 acceptance RED + contract design — harvest: зелено как есть, реализовано в VerifyAuthChallengeService._claim + claim_attempt + 401-конверт
- [S] approve stage-1 contracts — harvest
- [S] stage-2 implementation lanes — harvest
- [S] stage-3 acceptance GREEN + review — harvest

### 5.5 Верный код на последней разрешённой попытке всё ещё выдаёт сессию
<!-- review-origin: boundary -->
- [ ] stage-1 acceptance RED + contract design
- [ ] approve stage-1 contracts
- [ ] stage-2 implementation lanes
- [ ] stage-3 acceptance GREEN + review

### 5.3 Терминальное состояние отклоняет любой код и не оставляет следа
- [ ] stage-1 acceptance RED + contract design
- [ ] approve stage-1 contracts
- [ ] stage-2 implementation lanes
- [ ] stage-3 acceptance GREEN + review

### 5.4 Неизвестный идентификатор challenge отвечает ровно как истёкший
- [ ] stage-1 acceptance RED + contract design
- [ ] approve stage-1 contracts
- [ ] stage-2 implementation lanes
- [ ] stage-3 acceptance GREEN + review

### 6.1 Повтор внутри окна возвращает ту же сессию
- [ ] stage-1 acceptance RED + contract design
- [ ] approve stage-1 contracts
- [ ] stage-2 implementation lanes
- [ ] stage-3 acceptance GREEN + review

### 7.1 Два одновременных запроса кода дают одну заявку и один живой challenge
- [x] stage-1 acceptance RED + contract design — harvest: зелено как есть, реализовано в Lua ACQUIRE_COOLDOWN (SET NX EX) + _guard_cooldown до создания challenge
- [S] approve stage-1 contracts — harvest
- [S] stage-2 implementation lanes — harvest
- [S] stage-3 acceptance GREEN + review — harvest

### 7.2 Два одновременных верных кода дают ровно одну сессию
- [ ] stage-1 acceptance RED + contract design
- [ ] approve stage-1 contracts
- [ ] stage-2 implementation lanes
- [ ] stage-3 acceptance GREEN + review

### 7.3 Две одновременные проверки для нового email создают одного пользователя
- [ ] stage-1 acceptance RED + contract design
- [ ] approve stage-1 contracts
- [ ] stage-2 implementation lanes
- [ ] stage-3 acceptance GREEN + review

### 8.1 Время жизни проходит от конфигурации до сроков токенов без искажений
- [x] stage-1 acceptance RED + contract design — harvest: зелено как есть, реализовано в Challenge.create + ChallengeSettings.to_challenge_policy + SessionPolicy
- [S] approve stage-1 contracts — harvest
- [S] stage-2 implementation lanes — harvest
- [S] stage-3 acceptance GREEN + review — harvest

### 8.2 Остаток кулдауна отдаётся целыми секундами на всех границах
- [x] stage-1 acceptance RED + contract design — harvest: зелено как есть, реализовано в RedisChallengeStore._retry_after_seconds (ceil, минимум 1)
- [S] approve stage-1 contracts — harvest
- [S] stage-2 implementation lanes — harvest
- [S] stage-3 acceptance GREEN + review — harvest

### 8.4 Регистр и форма записи email — одна личность
- [x] stage-1 acceptance RED + contract design — harvest: зелено как есть, реализовано в Email.of (NFC+lower) + EmailCodeStrategy.subject_of/account_for
- [S] approve stage-1 contracts — harvest
- [S] stage-2 implementation lanes — harvest
- [S] stage-3 acceptance GREEN + review — harvest

## Tier 2 — Security Scenarios (05_Security_Tests.md)

### 1.1 Ввод сверх объявленных границ отклоняется до постановки заявки
- [ ] stage-1 acceptance RED + contract design
- [ ] approve stage-1 contracts
- [ ] stage-2 implementation lanes
- [ ] stage-3 acceptance GREEN + review

### 1.3 Инъекция в поля запроса не доходит до базы и не ломает запрос
- [x] stage-1 acceptance RED + contract design — harvest: зелено как есть, реализовано в Email.of/ChallengeId.of/PresentedSecret.of + параметризация SQLAlchemy
- [S] approve stage-1 contracts — harvest
- [S] stage-2 implementation lanes — harvest
- [S] stage-3 acceptance GREEN + review — harvest

### 1.4 Враждебный email не рвёт лог и не пересекается с чужим ключом
- [x] stage-1 acceptance RED + contract design — harvest: зелено как есть, реализовано в Email.of (ADDRESS_PATTERN режет CR/LF) + Email.masked
- [S] approve stage-1 contracts — harvest
- [S] stage-2 implementation lanes — harvest
- [S] stage-3 acceptance GREEN + review — harvest

### 2.1 Серверные поля, присланные клиентом, игнорируются
- [x] stage-1 acceptance RED + contract design — harvest: зелено как есть, реализовано в extra="ignore"/"forbid" на схемах + _issue_session
- [S] approve stage-1 contracts — harvest
- [S] stage-2 implementation lanes — harvest
- [S] stage-3 acceptance GREEN + review — harvest

### 2.2 Тип challenge без зарегистрированной стратегии отклоняется явно
- [x] stage-1 acceptance RED + contract design — harvest: зелено как есть, реализовано в ChallengeType.parse без дефолта + ChallengeStrategyRegistry.for_type
- [S] approve stage-1 contracts — harvest
- [S] stage-2 implementation lanes — harvest
- [S] stage-3 acceptance GREEN + review — harvest

### 3.1 Чужой идентификатор challenge не даёт ни сессии, ни сведений о существовании
- [x] stage-1 acceptance RED + contract design — harvest: зелено как есть, реализовано в VerifyAuthChallengeService._claim — тот же 401 на чужой challenge
- [S] approve stage-1 contracts — harvest
- [S] stage-2 implementation lanes — harvest
- [S] stage-3 acceptance GREEN + review — harvest

## Tier 2 — Infrastructure Scenarios (04_Infrastructure_Tests.md)

### 4.1 Приложение не стартует с негодной конфигурацией и называет переменную
- [ ] stage-1 acceptance RED + contract design
- [ ] approve stage-1 contracts
- [ ] stage-2 implementation lanes
- [ ] stage-3 acceptance GREEN + review
