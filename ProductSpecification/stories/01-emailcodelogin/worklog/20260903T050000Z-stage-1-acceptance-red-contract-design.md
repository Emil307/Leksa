# 4.1 Существующий пользователь получает сессию по верному коду — stage-1 acceptance RED + contract design

Started: 2026-09-03T05:00:00Z

Outcome: PASS — обе полосы сошлись, RED подтверждён, план Stage 2 прошёл gate

## Объявленное владение (до диспатча)

| Полоса | Владеет | Коммит |
|---|---|---|
| Acceptance RED | `acceptance/**` | 2e7b654 |
| Contract design | `backend/**`, `decisions/**`, `infrastructure/.env.example`, `setup-ports.sh` | 8c5ac53 |

Манифесты не пересекаются; ни одна полоса не писала в пути другой.

## Acceptance RED

Цель: `acceptance/tests/backend/auth/test_challenge_verify_acceptance.py::TestChallengeVerifyAcceptance`,
один кейс `test_should_issue_a_session_for_the_existing_user_without_creating_another` —
все Then сходятся в одном исполнении verify.

**Predicted failure:** `AssertionError: the code request must be accepted with 200, got 404`
в `challenge_verify_statements.py:43`.
**Actual failure:** совпал дословно — тип, сообщение, место, статус RED.

Петля прогнозов: первый прогноз («ConnectionRefused к Postgres») промахнулся — без экспорта
`infrastructure/.env` фикстура ушла в чужой Postgres на 5432. Второй («отказ соединения с 5433»)
промахнулся — БД этого репозитория поднята и на 8001 слушает живой бэкенд, у которого
`/api/v1/auth/challenge/start` отвечает 404. Третий совпал и воспроизведён повторным прогоном.

| Then | Statements-метод |
|---|---|
| пользователь зарегистрирован и получил код | `given_registered_user_holding_a_valid_code()` |
| ответ несёт идентификатор существующего пользователя | `assert_session_belongs_to_the_existing_user()` |
| ответ несёт id сессии, refresh- и access-токен | `assert_session_carries_identifier_and_both_tokens()` |
| нового пользователя не создаётся | `assert_no_second_user_was_created()` |

## Два отступления RED-полосы и их разрешение координатором

1. **Код читается из `notifications.t_outbox`, а не из MailHog.** Принято: воркера, разбирающего
   outbox, в репозитории нет, а `tests/01_API_Tests.md` прямо фиксирует строку outbox как
   единственный наблюдаемый выход `start` до отдельной истории доставки. Через MailHog тест не
   позеленел бы в Stage 3 никогда.
2. **Существующий пользователь засевается в БД, а не создаётся первым полным логином.** Принято:
   первый логин взводит кулдаун 60 с на этот email, снятия кулдауна успешным `verify` спецификация
   не обещает, второй `start` внутри минуты вернул бы 409. Засеянная форма — ровно та, которую
   гарантирует спека (`01_EmailCodeLogin.md`, «пользователь есть в `t_users`, строки `t_auth` нет»),
   и ADR проектной полосы покрывает её явной строкой: `issue_session` создаёт только строку `t_auth`,
   пользователя не дублирует, `created_user=False`. Противоречия между полосами нет.

## Contract design

Adapter discovery: `adapter_cache` (ChallengeVerificationStorePort не реализован),
`adapter_storage` (SessionIssuancePort, нет модели `auth.t_auth` и миграции),
`application` (AccessTokenIssuerPort, RefreshTokenGeneratorPort заглушены),
`adapter_rest` (эндпоинта `/verify` нет вовсе). `[S]`: ClockPort/IdGeneratorPort отгружены;
отображение исключений в конверт ошибок уже есть в `exception_handlers`.

ADR: `decisions/challenge-verify-contracts-decision.md`. Материальные решения — гашение challenge
в Redis, но сравнение кода в домене за постоянное время; разделение `find_challenge` →
`claim_attempt` → `redeem_challenge`; одна транзакция за границей `SessionIssuancePort.issue_session`;
личность через `strategy.account_for(uniqueness_key) -> ProviderAccount`, поэтому сервис остаётся
метод-агностичным; окно повтора представлено TTL записи, а не полем со сравнением на чтении;
строка сессии всегда новая, `created_user=False` — это и есть «нового пользователя не создаётся»;
JWT подписывается в композиционном корне.

Зафиксировано, но не чинится здесь: отгруженный обработчик `UnauthorizedException` отдаёт
`payload: null` и единое сообщение, что спорит с `endpoints.md` — разбирается на 5.1/5.4.

## Stage 2 Lane-Plan Gate

Проверено: манифесты разъединены, ни одной полосе не нужен новый выход соседа, чтобы
скомпилироваться и пройти свой фокусный цикл. Один осознанный узел: `SessionPolicy` строится
в настройках конструктором dataclass, а не через `SessionPolicy.of`, иначе полоса композиционного
корня зависела бы от доменной реализации полосы usecase.

<!-- stage-2-plan:
usecase: unit=verify-challenge use-case behaviour incl. the domain it delegates to; writes=[backend/domain/src/domain/auth/challenge/challenge_id.py: implement of, backend/domain/src/domain/auth/challenge/presented_secret.py: implement of, backend/domain/src/domain/auth/challenge/challenge_policy.py: implement replay_ttl_seconds, backend/domain/src/domain/auth/email_code/strategy.py: implement restore_secret/account_for, backend/domain/src/domain/auth/session/session_policy.py: implement access_expiry_at/refresh_expiry_at, backend/usecase/src/usecase/services/auth/verify_challenge.py: implement verify, backend/usecase/tests/services/auth/test_verify_challenge_issues_session.py: new focused test, backend/usecase/tests/usecase_testing/fakes/challenge_verification_store.py: new port fake, backend/usecase/tests/usecase_testing/fakes/session_issuance.py: new port fake, backend/usecase/tests/usecase_testing/fakes/token_issuers.py: new refresh-token + access-token fakes, backend/usecase/tests/usecase_testing/statements/auth_verify.py: new Statements]; frozen-surfaces=[ChallengeVerificationStorePort.{find_challenge,claim_attempt,redeem_challenge,remember_verification,find_verification}, StoredChallenge, ChallengeClaim, SessionIssuancePort.issue_session, SessionIssuanceRequest, IssuedSessionRecord, AccessTokenIssuerPort.issue, RefreshTokenGeneratorPort.generate, ClockPort.now, IdGeneratorPort.new_id, VerifyChallengeRequest, VerifiedSession, VerifyAuthChallengeService.__init__, ChallengeStrategy ABC incl. restore_secret/account_for, ChallengeVerification, ProviderAccount, AuthProvider, AccessTokenClaims, RefreshToken field set, SessionPolicy field set, ChallengePolicy field set]
adapter-cache: unit=Redis challenge-verification boundary; writes=[backend/adapters/cache/src/adapter_cache/verification_store.py: implement the five port methods, backend/adapters/cache/src/adapter_cache/verification_scripts.py: new Lua sources for claim/redeem, backend/adapters/cache/tests/test_redis_challenge_verification_store.py: new focused test, backend/adapters/cache/tests/cache_testing/statements/verification_store.py: new Statements]; frozen-surfaces=[ChallengeVerificationStorePort signatures, StoredChallenge, ChallengeClaim, ChallengeVerification, adapter_cache/keys.py templates, RedisChallengeStore record JSON field names, RedisChallengeVerificationStore.__init__]
adapter-storage: unit=Postgres identity-and-session issuance boundary; writes=[backend/adapters/storage/src/adapter_storage/repositories/session_issuance.py: implement issue_session in one transaction, backend/adapters/storage/src/adapter_storage/mappers/session_issuance.py: new insert-value mapping collaborator, backend/adapters/storage/src/adapter_storage/migrations/versions/<rev>_auth_accounts.py: new migration creating auth.t_auth with unique (provider, provider_id) and FK cascade from t_users, backend/adapters/storage/tests/test_session_issuance_repository.py: new focused test, backend/adapters/storage/tests/storage_testing/statements/session_issuance.py: new Statements]; frozen-surfaces=[SessionIssuancePort.issue_session, SessionIssuanceRequest, IssuedSessionRecord, ProviderAccount, AuthProvider.wire_value, AuthAccountEntity columns + indexes, UserEntity columns, SessionEntity columns, SQLAlchemyRepository API]
adapter-rest: unit=HTTP verify boundary; writes=[backend/adapters/rest/src/adapter_rest/routers/auth_verify.py: implement the handler body, backend/adapters/rest/src/adapter_rest/schemas/challenge_verify.py: implement from_usecase, backend/adapters/rest/tests/routers/test_auth_verify_router.py: new focused test over ASGITransport with a fake service, backend/adapters/rest/tests/rest_testing/auth_verify.py: new Statements/fake]; frozen-surfaces=[ChallengeVerifyRequest/ChallengeVerifyResponse field names + to_usecase/from_usecase signature, create_auth_verify_router signature, CHALLENGE_PREFIX, VerifyAuthChallengeService.verify signature, VerifiedSession, exception_handlers envelope]
application: unit=composition root; writes=[backend/application/src/application/security/jwt_access_token_issuer.py: implement issue, backend/application/src/application/security/refresh_token_generator.py: implement generate, backend/application/src/application/settings.py: register AuthTokenSettings on Settings + to_session_policy, backend/application/src/application/wiring.py: build get_verify_challenge_service, backend/application/src/application/main.py: mount create_auth_verify_router, backend/application/tests/test_app_factory.py: assert the verify route is exposed, backend/application/tests/test_security_tokens.py: new focused test for the JWT issuer and refresh-token generator]; frozen-surfaces=[AccessTokenIssuerPort.issue, RefreshTokenGeneratorPort.generate, AccessTokenClaims, SessionPolicy field set, VerifyAuthChallengeService.__init__, create_auth_verify_router, RedisChallengeVerificationStore/SessionIssuanceRepository constructors, ChallengePolicy, ChallengeStrategyRegistry]
-->

## Stage-2 prerequisite (не принадлежит ни одной полосе)

Координатор доводит до генерируемого `infrastructure/.env` четыре переменные (уже добавлены
проектной полосой в `.env.example` и `setup-ports.sh`), иначе регистрация `AuthTokenSettings`
в `Settings` уронит старт приложения:

```
AUTH_CHALLENGE_REPLAY_WINDOW_SECONDS=60
ACCESS_TOKEN_TTL_SECONDS=1800
REFRESH_TOKEN_TTL_SECONDS=31536000
JWT_SECRET=<локальное значение>
```

Туда же — добавление `PyJWT` в `requirements.txt` (`interview.md`, «NOT Yet Implemented»).

## Проверки после join

`ruff check backend acceptance` — All checks passed.
`lint-imports` — 1 contract kept, 0 broken.
`.venv/bin/python -m pytest backend -q` — 36 passed.
`.venv/bin/python -m pytest acceptance --collect-only -q` — 5 collected, новый тест skip-marked.
Ни один изменённый файл не превышает 200 строк.
