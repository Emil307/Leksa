# Stage 1 — acceptance RED + contract design (Story 4, Backend 4.1)

Invocation: `/continue story 4`
Outcome: `passed`
Сценарий: 4.1 «Опубликованный контракт описывает чтение профиля как защищённое»
(`<!-- review-origin: boundary -->` — блок порождён ревью stage-3 сценария 1.1, P2).

## Лейн «acceptance RED» — цель уже существовала

Файл `acceptance/tests/backend/contract/test_profile_contract_document_acceptance.py`
написан red-agent'ом на harvest и закоммичен в `744bf4f` с маркером отключения.
Писателя не дозапускали: цель полная и закрывает все четыре `Тогда/И` сценария —
схема `bearerAuth`, требование схемы операцией, ровно `200`/`401`, отсутствие
незащищённых вариантов чтения профиля.

Кейс один, RED наблюдён inline: маркер снят, прогон против рабочего бэкенда,
маркер восстановлен, дерево `acceptance/` чистое.

- Предсказание (текст маркера): `AssertionError — the contract must declare the
  security scheme bearerAuth as {'type': 'http', 'scheme': 'bearer',
  'bearerFormat': 'JWT'}, got None`.
- Наблюдение: то же дословно, `api_contract_statements.py:35`. Документ отдаётся
  (200), `components.securitySchemes` — пустой объект.
- Прогон: `1 failed, 75 passed, 3 skipped`; падает только целевой сценарий.

## Лейн «contract design»

Опубликованная схема **выводится из самого guard**, а не описывается рядом с ним:
`bearer_scheme = HTTPBearer(scheme_name="bearerAuth", bearerFormat="JWT",
auto_error=False)` объявлен в `access_token_guard.py`, и на Stage 2 guard берёт его
своей под-зависимостью. FastAPI собирает `security_requirements` по графу
зависимостей, поэтому `security` операции и запись в `components.securitySchemes`
появляются именно потому, что операция зависит от guard: забыть объявление, не
забыв защиту, нельзя. `auto_error=False` обязателен — `HTTPBearer` тогда ничего не
решает и не разбирает, отказ по-прежнему выносит `AuthenticateRequestService` по
сырому заголовку, счёт 4096 октетов остаётся до любого разбора.

Ключ `401` зависимостью не выводится (FastAPI не даёт зависимостям объявлять
ответы) — он остаётся `responses=` на маршруте, как уже сделано у `/health`.

Отвергнуто:

1. **Ручное объявление** `openapi_extra`/`security=` на маршруте плюс правка
   `securitySchemes` в `create_app` — второе независимое описание того же факта:
   маршрут может потерять guard и остаться «защищённым» в документе. Это ровно тот
   дефект, который чинится, переписанный в новом месте.
2. **Пост-обработка документа** хуком на `app.openapi` по маске пути `profile` —
   документ утверждал бы защиту по имени пути независимо от guard (fail-open в
   описании), и знание о путях REST-адаптера уехало бы в `application`.
3. `HTTPBearer(auto_error=True)` как настоящее принуждение — меняет поведение и
   разбирает заголовок раньше счёта октетов.

Проверено эмпирически на FastAPI 0.141.1: собранный документ даёт схему ровно из
трёх ключей, `security` операции `[{"bearerAuth": []}]`, ключи `responses` ровно
`200` и `401`. **`422` не появляется** — FastAPI добавляет его только при наличии
параметров или тела, а схема безопасности идёт в `security_requirements`.

Создано и изменено (скелет, без поведения):

- `backend/adapters/rest/src/adapter_rest/schemas/errors.py` — новый
  `UnauthorizedErrorResponse`: `code`/`message` как `Literal`, `payload` всегда
  `null`, `extra="forbid"`.
- `backend/adapters/rest/src/adapter_rest/security/access_token_guard.py` —
  добавлены `BEARER_SCHEME_NAME`, `BEARER_TOKEN_FORMAT` и объект `bearer_scheme`.
  Сигнатура `create_access_token_guard` и чтение сырого заголовка не тронуты.
- `ProductSpecification/stories/04-accesstokenguard/decisions/published-security-scheme-source-decision.md`.

## Stage 2 lane plan

Ровно одна архитектурная граница исполнения — REST-адаптер, поэтому одна полоса.

<!-- stage-2-plan:
adapter-rest: unit=REST adapter published-contract declaration; writes=[backend/adapters/rest/src/adapter_rest/routers/profile.py: add responses={401: {"model": UnauthorizedErrorResponse}} to the profile GET route, backend/adapters/rest/src/adapter_rest/security/access_token_guard.py: wire Security(bearer_scheme) into the guard signature so the operation publishes bearerAuth, backend/adapters/rest/tests/rest_testing/profile_statements.py: add when_the_published_contract_is_requested plus assertions on securitySchemes.bearerAuth, operation security and the exact 200/401 response keys, backend/adapters/rest/tests/routers/test_profile_router.py: add the focused cases driving those statements]; frozen-surfaces=[adapter_rest.security.access_token_guard.create_access_token_guard(authenticate_service) -> AccessTokenGuard, adapter_rest.security.access_token_guard.AUTHORIZATION_HEADER raw-header read, adapter_rest.security.access_token_guard.bearer_scheme = HTTPBearer(scheme_name="bearerAuth", bearerFormat="JWT", auto_error=False), adapter_rest.schemas.errors.UnauthorizedErrorResponse(code, message, payload), adapter_rest.schemas.profile.UserProfileResponse, adapter_rest.exception_handlers.UNAUTHORIZED_BODY]
-->

`backend/application/src` дельты не получает: роутеры уже смонтированы, объявление
целиком принадлежит REST-адаптеру. Композицию подаваемого документа проверяет
acceptance-тест — это Stage 3 composition verification, не зависимость Stage 2.

## Расхождение с утверждённым контрактом

`api-specs/profile_get.yaml` даёт `securitySchemes.bearerAuth` четырёхстрочный
`description`, а сценарий требует точного равенства объекта трём ключам. Передать
`description` в `HTTPBearer` нельзя. Расхождение осознанное и зафиксировано в
decision-файле: yaml остаётся проектной спецификацией с пояснениями, подаваемый
документ — машинным контрактом. Того же рода уже существующее расхождение —
имена компонентов (`UserProfileResponse` против `UserProfile`).

## Находка вне границ полосы

`backend/application/tests/application_testing/statements/app_factory.py:69` —
`assert_profile_route_is_mounted_as_a_guarded_read` по-прежнему не утверждает
ничего про guard, ровно как названо в P2. Все `Тогда/И` сценария 4.1 закрываются
на границе REST-адаптера плюс acceptance, поэтому файл в манифест полосы не
включён. Ужесточение или переименование — отдельное решение.

## Проверки

- `pytest backend` — 60 passed
- `pytest backend/adapters/rest backend/application` — 28 passed
- `ruff check backend/` — All checks passed
- import-linter — 1 kept, 0 broken
- приёмка — 75 passed, 4 skipped (маркер восстановлен)
