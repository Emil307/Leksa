# AccessTokenGuard

## Brief Description
Общий guard проверяет access JWT и активную сессию перед продуктовой ручкой.
`GET /api/v1/profile` возвращает владельцу токена всю строку `auth.t_users` в camelCase.

## Flow
1. Клиент вызывает `GET /api/v1/profile` с `Authorization: Bearer <token>`.
2. Guard принимает только JWT с алгоритмом HS256 и корректной подписью.
3. Guard валидирует `sub`, `sid`, `exp`, `aud`, `jti` и `aud = "uwords-api"`.
4. По `sid` из PostgreSQL читается сессия; она принадлежит `sub` и ещё не истекла.
5. По `sub` читается `auth.t_users`, после чего ручка отвечает профилем.
6. Любой отказ проверки возвращает единый `401` без раскрытия причины.

## Acceptance Criteria
- Корректный токен и активная сессия дают `200` со всеми полями `auth.t_users`.
- Поля ответа: `id`, `name`, `surname`, `email`, `isSuperuser`, `createdAt`,
  `updatedAt`, `avatarId`, `birthday`, `gender`, `city`, `phone`; nullable-поля равны `null`.
- Ручка не принимает `userId` и никогда не возвращает чужой профиль.
- Отсутствующий, повреждённый, подделанный, истёкший или неполный токен даёт точно
  `{code: "UNAUTHORIZED", message: "Unauthorized", payload: null}` с HTTP `401`.
- Неизвестная, истёкшая или принадлежащая другому `sub` сессия даёт тот же `401`.
- В ответах и логах нет JWT, refresh-токена, секрета подписи или лишних данных сессии.
- Текст профиля остаётся данными валидного UTF-8 JSON, а даты имеют locale-independent формат.

## Validation Rules
| Поле | Правило |
|---|---|
| `Authorization` | Bearer-схема с одним JWT, не более 4096 октетов |
| JWT header | разрешён только `alg = HS256` |
| `sub`, `sid`, `jti` | обязательные UUID |
| `exp` | Unix seconds `1..253402300799`; вне диапазона или `now >= exp` невалиден |
| `aud` | обязательная строка `uwords-api` |
| session | существует, `user_id = sub`, при `now >= expires_at` истекла |

## Screen States
- UI не входит в историю; внешние состояния API — `200` и единый `401`.

## Core Requirements
- HS256-секрет обязателен в конфигурации; отсутствие или пустое значение ломает старт.
- Время проверяется через внедряемые часы в UTC, включая точную границу истечения.
- Активная сессия читается из PostgreSQL на каждом запросе, без локального кеша.
- Ошибка или недоступность проверки авторизации никогда не разрешает запрос.
- Каждый отказ даёт безопасный внутренний reason-code без токена/PII; успех его не пишет.
- `jti` проверяется как UUID, но denylist в этой истории не создаётся.
- Выпуск/refresh/logout, роли, rate limiting и `learner.t_profiles` вне scope.
