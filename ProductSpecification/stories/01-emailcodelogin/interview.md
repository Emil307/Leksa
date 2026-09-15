# Story 01 — EmailCodeLogin: контекст интервью

Вход в приложение по email без пароля: пользователь вводит почту, получает
6-значный код, вводит его — и получает сессию.

## Scope

**В скоупе:**

- Две ручки: `start` (создать challenge + отправить код) и `verify` (проверить код + выдать сессию).
- Единственный тип challenge — `EMAIL_CODE`.
- Время жизни кода, счётчик неудачных попыток, лимит попыток.
- Кулдаун на повторную отправку кода.
- Убийство предыдущих challenge того же пользователя при создании нового.
- Авторегистрация: неизвестный email становится пользователем при успешном verify.
- Выпуск сессии: refresh token (год) + access token (30 минут).

**Вне скоупа (явные не-цели этой истории):**

- Вход через **Telegram** и **Google** — значения `TG` и `OAUTH` в enum `challengeType` появятся позже.
  Поэтому в enum пока **только** `EMAIL_CODE`.
- Поле `authorizeUrl` в ответе `start` — появится вместе с OAUTH. Сейчас его в контракте **нет**.
- Значение `status` (`AUTHENTICATED`) в ответе `start` — появится вместе с TG. Сейчас его в контракте **нет**.
- **Логаут** — отдельная история.
- **Ротация refresh-токена и обновление access-токена** — отдельная история.
- Профиль и онбординг (`learner.t_profiles`, `learner.t_onboarding`) — авторегистрация их не трогает.
- Защита от массового спама почты сверх кулдауна 60 сек (лимиты по IP, капча).

## API Endpoints

| Метод | Путь | Статус |
|---|---|---|
| POST | `/auth/challenge/start` | NOT YET IMPLEMENTED |
| POST | `/auth/challenge/verify` | NOT YET IMPLEMENTED |

Точные пути и схемы закрепит `/api-spec` — здесь зафиксированы тела.

**`start` request:**

```json
{ "email": "string", "challengeType": "EMAIL_CODE" }
```

**`start` response:**

```json
{
  "challengeId": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "challengeType": "EMAIL_CODE",
  "expiresAt": "2026-08-03T11:40:01.161Z"
}
```

**`verify` request:**

```json
{ "challengeId": "3fa85f64-5717-4562-b3fc-2c963f66afa6", "code": "123456" }
```

DECISION: verify принимает только `challengeId` + `code`. Тип challenge и email
восстанавливаются из самого challenge — клиент их не дублирует и не может подменить.

**`verify` response:**

```json
{
  "user": { "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6" },
  "session": {
    "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "refreshToken": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "accessToken": "string"
  }
}
```

DECISION: имена полей идут за схемой БД — `user.id`, `session.id`, а не `userId`/`sessionId`.
`userId` внутри `session` не дублируется: он уже есть рядом в `user.id`.

## Token / Auth Requirements

- **accessToken** — JWT **HS256**, payload `sub = user.id`, `sid = session.id`, `exp`. Живёт **30 минут**.
  Секрет — из конфигурации (`pydantic-settings`), не хардкод.
- **refreshToken** — случайный непрозрачный токен, хранится в `auth.t_sessions.refresh_token`.
  Живёт **1 год**. Единственный источник правды — строка в БД, не содержимое токена.
  ACTION: срок жизни считается от `created_at`; если этого мало — добавить `expires_at` при написании миграции.

## Key Architectural Decisions

DECISION: **Хранилище challenge — Redis.** Челлендж и код лежат вместе одной записью с TTL,
равным времени жизни кода. Истечение TTL = смерть челленджа, отдельного сборщика мусора нет.

DECISION: **Redis добавляется в стек этой историей** — сейчас его нет нигде: ни в
`ProductSpecification/technology.md`, ни в `infrastructure/docker-compose.yml`, ни в
`infrastructure/.env`, ни в `requirements.txt`.
ACTION: новый адаптер `backend/adapters/cache` (redis-py asyncio), сервис `redis` в compose,
`REDIS_PORT` в `.env`/`setup-ports.sh`, строка в `technology.md`, порт в `usecase.ports`.

DECISION: **Redis настраивается как долговечное хранилище: `appendonly yes` + `appendfsync everysec`,
`maxmemory-policy noeviction`.** Восстановление из отстающего RDB-снапшота способно вернуть погашенный
challenge и выдать по одному коду вторую сессию; `allkeys-lru` способна выбросить живой challenge,
оставив кулдаун, и запереть человека до конца минуты. Дефолт образа даёт `noeviction`, но не даёт AOF;
закрепляются оба, чтобы позднейшая экономия памяти не сняла ни одно из них молча.
ACTION: флаги в сервисе `redis`; утверждение читает `CONFIG GET` на запущенном сервисе, а не compose-файл.

DECISION: **Хранилища остаются как есть: challenge в Redis, очередь писем в Postgres.** Рассмотрены и
отклонены два варианта. Очередь в Redis убрала бы двойную запись Redis→Postgres — challenge и строка
очереди легли бы одним скриптом, — но сделала бы наименее долговечным ровно тот компонент, который
заведён ради переживания лежащего SMTP. Челленджи в Postgres превратили бы очередь в настоящий outbox
с одной транзакцией, но убрали бы Redis из стека целиком. Двойная запись остаётся принятой: её худший
исход — человек не получил письмо и нажал «отправить снова».

DECISION: **Выбор ветки по `challengeType` — через стратегию.** Один интерфейс стратегии на тип
челленджа; `EMAIL_CODE` — единственная реализация сейчас. TG и OAUTH добавляются новой стратегией,
не ветвлением в сервисе.

CROSS-STORY DECISION: все будущие провайдеры сохраняют общие
`/api/v1/auth/challenge/start` и `/api/v1/auth/challenge/verify`. В частности,
отдельного `/api/v1/auth/telegram/exchange` не будет; Telegram добавляет стратегию
`TG`. См. [ADR границы клиентов](../../tasks/1-refactoring-bot-api-boundary/decisions/unified-client-auth-decision.md).

DECISION: **Убийство прошлых челленджей происходит ПОСЛЕ выбора стратегии.** Ключ уникальности,
по которому ищутся живые челленджи, принадлежит стратегии: для `EMAIL_CODE` это email, для TG и
OAUTH это будут другие данные. Сервис не знает, что ключ — это email.

DECISION: **Проверка кода и его удаление — одна атомарная операция в Redis** (Lua-скрипт или
эквивалент). Иначе два параллельных verify с верным кодом выпустят две сессии.
Инкремент счётчика попыток — в той же атомарной операции.

DECISION: **Идентификаторы — UUID.** `auth.t_users.id`, `auth.t_auth.id`, `auth.t_sessions.id`
и их FK становятся `uuid`. `docs/db-schema.sql` пока показывает `INTEGER IDENTITY`.
ACTION: миграция пишется под UUID, и `docs/db-schema.sql` приводится в соответствие.

DECISION: **Авторегистрация — на verify, не на start.** Пользователь появляется в `auth.t_users`
только после подтверждённого кода. Никто не может наплодить пустых пользователей, просто дёргая `start`.

DECISION: `auth.t_users.name` заполняется **пустой строкой** — колонка `NOT NULL`, а настоящего
имени при passwordless-входе взять неоткуда. Имя появится в онбординге.

DECISION: **Строка в `auth.t_auth` создаётся** для email-провайдера: `provider = 'email'`,
`provider_id = email`. Схема уже обновлена — колонки `access_token`/`refresh_token` из `t_auth`
удалены, они там были не нужны.
ACTION: `provider_id` сейчас `UNIQUE` глобально, а не в паре с `provider`. При добавлении
telegram/google это столкнёт разные провайдеры в одном пространстве идентификаторов —
уникальность нужно перенести на `(provider, provider_id)`.

DECISION: **Сессий у пользователя может быть много** — каждый успешный verify создаёт новую строку
в `auth.t_sessions`. Вход с нового устройства не выкидывает со старого. `fingerprint` из схемы
удалён, уникальный индекс `(user_id, fingerprint)` заменён на обычный по `user_id`.

DECISION: **Авторегистрация создаёт только `auth.t_users`** (+ `auth.t_auth`). `learner.t_profiles`
требует выбора языков, который делается на экранах онбординга — вход туда не лезет.

## Business Rules & Constraints

- Код — **6 цифр**.
- Время жизни кода = время жизни челленджа = **5 минут**. `expiresAt` в ответе `start` — это оно.
- **5 неудачных попыток** verify — после пятой челлендж удаляется, нужен новый `start`.
- **Кулдаун 60 секунд** между отправками кода на один email. Повторный `start` раньше — ошибка.
- Новый `start` **убивает все живые челленджи** с тем же ключом уникальности. Старый код
  перестаёт работать сразу, не дожидаясь своего TTL.
- Успешный verify **удаляет** челлендж — повторный вход по тому же коду невозможен.
- Ошибки verify различаются по коду, но **остаток попыток наружу не отдаётся**:
  - неверный код → `UNAUTHORIZED`
  - челлендж истёк или не найден → `UNAUTHORIZED` (отдельным сообщением)
  - попытки исчерпаны → `UNAUTHORIZED` (отдельным сообщением)
- Невалидный формат email на `start` → `VALIDATION_FAILED`.
- `challengeType` вне enum → `VALIDATION_FAILED`.

## Already Implemented (REUSE)

- `domain.errors` — `BaseDomainException`, `ErrorCode` (`VALIDATION_FAILED`, `UNAUTHORIZED`, …)
  и централизованный `register_exception_handlers` в `adapter_rest/exception_handlers.py`.
  Новых механизмов ошибок не заводим.
- `usecase.ports.notifications.email.EmailSenderPort` + `adapter_email.sender.SmtpSender` (aiosmtplib, MailHog в dev) —
  отправка кода уже есть чем делать, порт не переизобретаем.
- `adapter_storage`: `UnitOfWork`, `SQLAlchemyRepository` (`get_one`/`add_one`/`update_one`/`delete_one`),
  Alembic настроен, `models/` пуст — первые модели будут наши.
- `application/wiring.py` — ручное связывание через `lru_cache`-фабрики.

**Текущее состояние продукта:** acceptance-сьют содержит ровно один включённый тест —
`TestHealthAcceptance` (`/health` отвечает 200). Никакой авторизации в продукте сейчас нет.

## NOT Yet Implemented (Gaps)

- Redis: инфраструктура, зависимость, адаптер, порт, настройки.
- ORM-модели и миграция для `auth.t_users`, `auth.t_auth`, `auth.t_sessions` (с UUID).
- Домен: `Email`, `VerificationCode`, `Challenge`, `Session` и их правила.
- Usecase: старт челленджа, верификация челленджа, стратегии по `challengeType`.
- Генерация JWT (библиотека для подписи HS256 в `requirements.txt` отсутствует).
- REST-роутер `auth` + Pydantic-модели запроса/ответа.
- Acceptance-клиент и Statements для авторизации; чтение письма из MailHog в тестах.

## Cross-Story Dependencies

- **Зависимостей от других историй нет** — это первая история продукта.
- **От неё зависят:** логаут, ротация/обновление токенов, вход через Telegram, вход через Google,
  онбординг и профиль — всё, что требует авторизованного пользователя.
- Enum `challengeType` и стратегия проектируются так, чтобы TG и OAUTH добавлялись без
  переписывания `start`/`verify`.

## Testing Considerations

- Код из письма в acceptance-тестах вычитывается из **MailHog** по HTTP API (`MAILHOG_HTTP_PORT`),
  а не подсматривается в Redis — тест должен остаться чёрным ящиком.
- Истечение TTL: тест не ждёт 5 минут — время жизни выносится в конфигурацию, и сценарий
  «код истёк» использует укороченное значение либо контролируемые часы.
- Redis нужен acceptance-сьюту и adapter-тестам хранилища — он поднимается тем же
  `infrastructure/scripts/run-infra.sh`.
- Гонку «два параллельных verify с верным кодом» проверяем явным сценарием: ровно одна сессия.

## Performance / Rate Limits

- `ProductSpecification/ExpectedLoad.md` пока не заполнен — цифр нагрузки нет.
- Единственное явное ограничение частоты в этой истории — кулдаун 60 сек на отправку кода
  на один email. Всё остальное (лимиты по IP, глобальный throttling) — вне скоупа.
- Приложение работает в нескольких инстансах: счётчики попыток и кулдаун живут в Redis,
  никакого in-memory состояния.
