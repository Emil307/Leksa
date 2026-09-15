# AccessTokenGuard — эндпоинты API

| Метод | Путь | Описание |
|---|---|---|
| GET | `/api/v1/profile` | Проверить access JWT и активную сессию, вернуть текущему пользователю всю строку `auth.t_users` в camelCase |

Спецификация: `ProductSpecification/api-specs/profile_get.yaml`.

## Контракт авторизации

- Единственное предъявляемое полномочие — `Authorization: Bearer <JWT>` длиной не
  более 4096 октетов. Разрешён только HS256; обязательны UUID-claims `sub`, `sid`,
  `jti`, целочисленный `exp` и строковый `aud = "uwords-api"`.
- Guard на каждом запросе читает `auth.t_sessions`. Сессия должна существовать,
  принадлежать `sub` и иметь `expires_at` строго позже текущего момента.
- Любой отказ — от заголовка и JWT до недоступности проверки сессии — возвращает
  ровно `401 {"code":"UNAUTHORIZED","message":"Unauthorized","payload":null}`.
  Причина, токены, claims и PII наружу не попадают.

## Ответ профиля

Успех возвращает непосредственно запись `auth.t_users`, без внешнего envelope:
`id`, `name`, `surname`, `email`, `isSuperuser`, `createdAt`, `updatedAt`,
`avatarId`, `birthday`, `gender`, `city`, `phone`. Все свойства присутствуют;
nullable-колонки представлены JSON `null`.

Ручка не принимает request body, path-параметры или контрактный query-параметр
`userId`. Профиль всегда выбирается по проверенному `sub`; присланное клиентом
значение не может выбрать другого пользователя. Данные `learner.t_profiles`,
сессии и токены в ответ не добавляются.

## Текущее состояние

Во включённом acceptance-сьюте описан только `/health`; в REST-коде существует
только health-router. Guard и `/api/v1/profile` пока не реализованы.
