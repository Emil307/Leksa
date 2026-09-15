# Decision: Контракты ротации токенов сессии

**Date**: 2026-08-16 **Scenarios**: 2.1

Сценарий 2.1 — первый код сессий: `auth.t_sessions`, домен `Session`, порты и REST-контракт
обязаны быть заморожены разом, иначе независимые полосы Stage 2 не смогут стартовать вместе.

| Rejected | Why |
|----------|-----|
| Наивный `SELECT`, затем `UPDATE` как решающая проверка | Два инстанса приняли бы один токен; авторитетом обязан быть счётчик изменённых строк одного условного `UPDATE`. |
| Условный `UPDATE` без предварительного чтения, подпись после записи | `sub`/`sid` неизвестны до чтения; подпись после коммита гасит ещё действующий refresh-токен при ошибке подписи. |
| Отдельная дистрибуция `adapter_security` под подпись JWT | Новый модуль не попадает в `requirements.txt`, а корневые файлы установки принадлежат координатору; реализация живёт в композиционном корне — так же, как часы и генераторы в решении `EmailCodeLogin`. |
| `JWT_ALGORITHM` как настройка | Значение `none` отключило бы подпись, и ни одна boot-проверка не выглядела бы неправильной; алгоритм — константа выпускающего. |
| `extra="forbid"` на Pydantic-схеме запроса | Лишнее поле дало бы 422 FastAPI вместо отгруженного конверта `{code, message, payload}` с 400. |
| Сравнение срока по `now()` базы | Тесты границы истечения и скользящего года перестали бы управляться внедряемыми часами; принят единый `now`, прочитанный один раз за запрос. |
| Создать здесь же `auth.t_users` и FK | Таблица принадлежит `EmailCodeLogin`; вместо этого зафиксирована семантика `ON DELETE CASCADE`, чтобы у той миграции не осталось открытого выбора. |
| Ждать `EmailCodeLogin` с миграцией `auth.t_sessions` | История 5 не имеет строки сессии и не может стартовать; эта ревизия — единственный создатель таблицы, ревизия истории 1 присоединяется к ней. |

**Chosen**: домен владеет алфавитом токена, границей истечения и скользящим сроком; usecase
чеканит и подписывает всю пару **до** записи, затем выполняет одну условную запись, чей счётчик
изменённых строк решает исход; storage-адаптер параметризован и меняет `refresh_token`,
`expires_at` и `updated_at` одним оператором; REST остаётся тонким переводчиком с allowlist из
одного свойства.

## Model

**domain.auth**

- `RefreshToken` — `of(raw)`: только печатный ASCII, поэтому 512 одновременно символы и байты;
  значение отвергается целиком (без усечения и `U+FFFD`); `matches()` — постоянное время;
  `__repr__`/`__str__` затёрты.
- `SessionPolicy` — `of(access, refresh)` отвергает неположительное и переполняющее значение;
  `access_expiry_at`/`refresh_expiry_at`; `truncate(now)` — floor до целой секунды, направление
  округления названо явно.
- `Session` — `is_expired_at` (граница включительна: `expires_at <= now`), `rotate` (тот же `id`
  и `user_id`), `access_token_claims`.
- `AccessTokenClaims` — ровно `sub`, `sid`, `exp`; `numeric_date()` в целых секундах UTC.

**usecase**

- `SessionRepositoryPort` — `find_active_by_refresh_token` (неавторитетное чтение ради ранней
  чеканки пары) и `rotate_refresh_token` (одна условная запись, `True` только при ровно одной
  изменённой строке).
- `RefreshTokenGeneratorPort`, `AccessTokenIssuerPort`; `ClockPort` переиспользуется.
- `RefreshSessionRequest(refresh_token)` — единственное входное поле; `RotatedSessionTokens`
  с затёртым `repr`.
- `RefreshSessionTokensService.refresh()`.

**adapters**

- `adapter_storage`: `SessionEntity` (`auth.t_sessions`, ширина колонки — доменная
  `MAX_TOKEN_BYTES`, уникальный индекс на `refresh_token`), `SessionMapper`,
  `SessionRepository`, ревизия `0001_auth_sessions`; `DbSettings.statement_timeout_seconds`
  задаёт конечный бюджет запроса.
- `adapter_rest`: `SessionRefreshRequest` (allowlist из одного свойства, лишние поля → 400),
  `SessionRefreshResponse`/`RotatedSessionSchema` (`extra="forbid"`), `create_auth_token_router`.
- `application`: `JwtAccessTokenIssuer` (HS256-константа, секрет как `SecretStr`),
  `SecretsRefreshTokenGenerator`, `SystemClock`, `AuthTokenSettings`.

## Edge Cases

| Case | Behavior |
|------|----------|
| Лишнее серверное поле в теле | Отвергается по allowlist, не по перечислению — 400 `VALIDATION_FAILED` |
| `refreshToken` отсутствует, `null` или не строка | Адаптер отображает в пустую строку, домен отвергает — 400 |
| Истёкший, неизвестный, использованный, проигравший гонку токен | Ноль изменённых строк → одинаковый 401 `UNAUTHORIZED`, сессия не меняется |
| Ошибка генерации или подписи | Возникает до записи — старый refresh-токен остаётся действительным |
| Ошибка БД или незафиксированная транзакция | 503 `UNAVAILABLE`; `refresh_token` и `expires_at` откатываются вместе |
| Сгенерированный токен | Проходит через `RefreshToken.of` перед записью — тот же алфавит и та же граница, что у предъявленного |
| Часы инстансов расходятся | Принятый риск: `now` читается один раз за запрос из внедряемых часов, синхронизация — операционное требование NTP |

## Дополнение 2026-09-14: уникальный идентификатор access-токена

Stage 3 показал, что login и refresh в одну секунду выпускают побайтно одинаковый access-JWT:
`sub`/`sid`/`exp` совпадают, а `exp` усечён до секунды. Обязательство «новая пара» (поток п.2/п.4)
нарушено. Guard Story 4 (`VerifiedAccessToken.of`) к тому же требует `jti` и `aud` — токен без
них непригоден для защищённых маршрутов.

| Rejected | Why |
|----------|-----|
| `iat` в миллисекундах как источник уникальности | JWT `iat` — целые секунды (RFC 7519 NumericDate); два выпуска в одну секунду снова совпали бы. |
| Случайный `jti` внутри `JwtAccessTokenIssuer` без участия домена | Usecase-тесты не могли бы утверждать, что каждый выпуск получает свежий идентификатор; источник идентификаторов уже есть — `IdGeneratorPort`. |

**Chosen**: `AccessTokenClaims` получает `tokenId` (UUID). Usecase берёт его из `IdGeneratorPort`
на каждый выпуск — и при входе (`VerifyAuthChallengeService`), и при ротации
(`RefreshSessionTokensService`, конструктор дополнен портом). `JwtAccessTokenIssuer` подписывает
`sub`, `sid`, `jti`, `exp` и константную аудиторию `aud = uwords-api` (`VerifiedAccessToken.API_AUDIENCE`),
так что выпущенный токен принимается guard'ом Story 4. Набор claims фиксирован ровно этими пятью.

## Дополнение 2026-09-14: чтение строки сессии в Integration-сценарии 1.1

Then-клаузы 1.1 («в той же строке хранилища совместно сохранены новый refresh-токен и новый
срок», «старый refresh-токен больше не действует» без изменения строки) не наблюдаемы ни через
один HTTP-маршрут: `refresh_token` и `expires_at` строки `auth.t_sessions` наружу не отдаются.

| Rejected | Why |
|----------|-----|
| Проверять только через REST (ответ + повтор старого токена) | Не доказывает атомарность записи одной строки и неизменность `expires_at` при отказе — суть интеграционного сценария. |
| Отдельный диагностический маршрут для чтения строки | Расширяет поверхность API ради теста; противоречит allowlist-контракту. |

**Chosen**: Statements интеграционного сценария читают строку напрямую через `AuthDatabase`
(asyncpg, read-only `SELECT refresh_token, created_at, expires_at`), по прецеденту
`authorization_header_statements.py` и `challenge_verify_registration_statements.py`. Запись в
хранилище из Statements по-прежнему только через `open_session`/`delete_session`-подготовку.
