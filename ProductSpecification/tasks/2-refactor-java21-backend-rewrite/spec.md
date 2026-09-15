# Task 2: Java 21 Backend Rewrite

Type: refactor

## Problem

Бэкенд написан на Python 3.12 / FastAPI с полностью асинхронным стеком
(SQLAlchemy async, asyncpg, aiosmtplib, redis.asyncio). Проект переходит на
Java 21 без реактивности: дальнейшая разработка историй должна вестись в
Spring-стеке, для которого в репозитории уже лежит биндинг
`.claude/tech/java-spring/`, а не в Python-стеке.

Пока бэкенд остаётся на Python, биндинг не используется, а два стека в
`ProductSpecification/technology.md` расходятся с реальностью репозитория.

## Solution

Перенести все backend-модули на Java 21 / Spring Boot 3 (Web MVC, без
реактивности), сохранив внешне наблюдаемое поведение без единого изменения:
те же HTTP-маршруты, коды статусов, тела запросов и ответов, заголовки,
та же схема БД, те же правила аутентификации и те же письма.

Критерий приёмки — существующий Python acceptance-набор (`acceptance/`,
чистый HTTP black-box) полностью зелёный против Java-бэкенда без правок
самих тестов. Правка acceptance-теста в ходе этой задачи означает изменение
поведения и запрещена: такой случай реклассифицируется в отдельную задачу.

Целевой стек:

| Слой | Технология |
|---|---|
| Язык | Java 21 (virtual threads вместо реактивности) |
| Сборка | Gradle, многомодульный проект |
| Web | Spring Boot 3, Spring Web MVC |
| Персистентность | Spring Data JPA + PostgreSQL |
| Миграции | Liquibase |
| Кэш | Redis (решение по клиенту принимается на этапе design) |
| Почта | SMTP, MailHog в dev (решение по клиенту принимается на этапе design) |
| Тесты | JUnit 5, Statements/Fakes по шаблонам биндинга |

Модульная структура сохраняется один в один: `backend/domain`,
`backend/usecase`, `backend/adapters/{rest,storage,email,cache}`,
`backend/application`. Направление зависимостей строго внутрь, как сейчас.

## Constraints

- Внешне наблюдаемое поведение не меняется. Acceptance-тесты не редактируются.
- Acceptance-набор остаётся на Python; порт его на Java — отдельная задача.
- Java-код растёт параллельно с Python-кодом; Python-бэкенд остаётся
  работоспособным и запускаемым до последнего шага задачи, который удаляет его
  целиком одним коммитом. До этого шага в любой момент есть рабочий бэкенд для
  сравнения поведения.
- Схема БД не меняется. Liquibase-changelog воссоздаёт текущую схему с нуля
  (`auth_users`, `auth_sessions`, `auth_accounts`, `notifications_outbox` и
  индексы), Alembic-миграции удаляются вместе с Python-кодом. Baseline на
  существующую БД не требуется.
- Unit-тесты портируются полностью — usecase, rest, storage, cache, email,
  application, вместе со Statements и Fakes.
- Истории 01 EmailCodeLogin, 04 AccessTokenGuard, 05 SessionRenewal,
  06 Telegram заморожены. Мигрируется только уже зелёное поведение;
  незакрытые чекбоксы этих историй не выполняются в рамках задачи и
  продолжаются после неё уже на Java. Спеки, decisions и `tests/*.md` историй
  переиспользуются как есть — они написаны на доменном языке.
- `bot/` и `frontend/` не затрагиваются: бот общается с бэкендом по HTTP и
  имеет собственную БД.
- `ProductSpecification/technology.md` переписывается на java-spring в рамках
  задачи; `.claude/**` не переводится и не правится.
- Инфраструктура меняется только через `infrastructure/` (compose, скрипты,
  порты из `infrastructure/.env`).

## Key Files

- `ProductSpecification/technology.md` — профиль стека и все команды
- `.claude/tech/java-spring/` — шаблоны, на которые опирается перенос
- `backend/domain/src/domain/{auth,common,notifications}/` — 36 типов домена
- `backend/usecase/src/usecase/{ports,services}/` — 6 сервисов, 14 портов
- `backend/adapters/rest/src/adapter_rest/{routers,schemas,security}/`
- `backend/adapters/storage/src/adapter_storage/{models,mappers,repositories,migrations}/`
- `backend/adapters/cache/src/adapter_cache/` — Redis, Lua-скрипты challenge-стора
- `backend/adapters/email/src/adapter_email/` — SMTP-отправитель
- `backend/application/src/application/{main,wiring,settings,system,security}`
- `acceptance/` — критерий приёмки, не редактируется
- `infrastructure/docker-compose.yml`, `infrastructure/scripts/` — запуск и тесты
- `pyproject.toml`, `.importlinter`, `requirements*.txt` — удаляются на последнем шаге
