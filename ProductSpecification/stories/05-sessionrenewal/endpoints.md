# SessionRenewal — эндпоинты API

| Метод | Путь | Описание |
|---|---|---|
| POST | `/api/v1/auth/token/refresh` | Атомарно ротировать refresh-токен существующей сессии и выпустить новый access-токен |

Спецификация: `ProductSpecification/api-specs/auth_token_refresh.yaml`.

## Таксономия ошибок

Все отказы используют существующий конверт `{code, message, payload}` из
`adapter_rest/exception_handlers.py`.

| Условие | HTTP | `code` | Побочный эффект |
|---|---:|---|---|
| Тело отсутствует или не JSON; `refreshToken` отсутствует, `null`, пустой, не ASCII, длиннее 512 байт; присутствуют лишние поля | 400 | `VALIDATION_FAILED` | Сессии не меняются |
| Refresh-токен истёк, неизвестен, уже использован или проиграл конкурентную ротацию | 401 | `UNAUTHORIZED` | Сессии не меняются; новая пара победителя остаётся действительной |
| БД недоступна или транзакция не зафиксировалась | 503 | `UNAVAILABLE` | Старый refresh-токен и прежний `expires_at` остаются действительными |

Истёкший, неизвестный и использованный токены имеют полностью одинаковые статус,
`code`, `message` и `payload`; токен и причина отказа наружу не попадают.

## Заметки

- Endpoint не требует `Authorization`: единственное предъявляемое полномочие —
  `refreshToken` в JSON-теле. Действующий или истёкший access-токен не принимается.
- Успех возвращает только `session {id, refreshToken, accessToken}`. `user`,
  `userId`, `expiresAt` и другие серверные поля не дублируются.
- Новых endpoint нет: logout, управление сессиями, access-token guard, cookie и
  клиентская координация остаются вне истории.

## Текущее состояние

Включённый acceptance-сьют описывает только `/health`; в
`backend/adapters/rest/src/adapter_rest/routers/` сейчас есть только `health.py`.
Форма сессии и токенов наследуется от `EmailCodeLogin`.
