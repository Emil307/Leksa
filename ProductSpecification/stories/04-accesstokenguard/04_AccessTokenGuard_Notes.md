# AccessTokenGuard — Notes & Considerations

## Warnings

### Functional Warnings

- JWT проходит только когда одновременно живы и `exp`, и строка сессии; более ранняя
  из двух границ прекращает доступ.
- Текущая `docs/db-schema.sql` ещё не содержит `auth.t_sessions.expires_at`. Story 1
  уже требует эту колонку; Story 4 не должна предполагать, что она появилась сама.
- Пользователь определяется только из `sub`. Любой присланный клиентом `userId` не
  участвует в выборе профиля.
- `Authorization` длиннее 4096 октетов отклоняется единым `401` до JWT decode и
  до обращения к PostgreSQL; лимит измеряется по wire bytes, а не по code points.

### Technical Warnings

- Алгоритм декодирования задаётся серверным allow-list `HS256`, а не читается как
  разрешение из JWT header; иначе возможна algorithm-confusion атака.
- Ошибки парсинга, подписи, claims и сессии схлопываются в один клиентский контракт.
  Диагностика не должна возвращать разные сообщения или внутренние идентификаторы.
- Профиль содержит PII. Его можно отдавать только владельцу проверенного `sub`, а
  значения email, телефона и токена нельзя включать в auth-error логи.
- Строки профиля сериализуются структурным JSON encoder. Кавычки, backslash,
  управляющие символы и injection-последовательности остаются строковыми данными
  и не меняют JSON, заголовки или логи.

---

## Suggestions & Future Enhancements

### Technical Suggestions

- Добавлять Redis read model активных сессий только после измеренной проблемы с
  чтением PostgreSQL. Он обязан сохранять немедленный отзыв и multi-instance
  согласованность; TTL-only кеш без invalidation для этого не подходит.
- Отдельный denylist `jti` возможен в истории точечного отзыва access-токенов.

---

## Technical Notes

### Current State

- В acceptance-сьюте включён только `TestHealthAcceptance`; защищённых ручек нет.
- JWT validator, auth context, user/session ports, ORM-модели, repositories,
  профильный usecase/router и их wiring ещё не реализованы.
- Повторно используются `UnauthorizedException`, централизованный error handler,
  `UnitOfWork`, SQLAlchemy repository base и router-factory wiring.

### Token and Session Contract

- Access JWT: HS256; `sub`, `sid`, `jti` — UUID; `exp` — Unix timestamp;
  `aud = "uwords-api"`.
- Сессия активна, когда строка существует, `user_id` совпадает с `sub` и
  `expires_at` строго позже текущего момента.
- Проверки `exp` и `expires_at` используют одни внедряемые часы; прямой вызов
  системного времени в доменной логике не нужен.
- Единый параметризованный guard проверяет обе временные границы за единицу до,
  точно в момент и за единицу после. Для `exp` он также проверяет `0`, отрицательное,
  `253402300800` и число больше `2^53`: любой unsupported value даёт `401`, не `500`.
- `jti` подтверждает форму токена, но не хранится и не используется для отзыва.

### Response Contract

- Storage возвращает доменную модель пользователя; REST schema отдельно задаёт
  camelCase aliases и не сериализует ORM-модель напрямую.
- Nullable-колонки остаются JSON `null`; сервер не подставляет learner-данные или
  вычисленные значения.
- JSON кодируется как UTF-8; multibyte, emoji и combining-form текст возвращаются
  byte-exact относительно сохранённого значения. Нормализация относится к write
  boundary и не выполняется этой read-only ручкой.
- `createdAt`/`updatedAt` имеют RFC 3339 UTC с `Z`, `birthday` — `YYYY-MM-DD`;
  результат не зависит от locale и timezone процесса.
- Все auth-отказы: HTTP `401`, `code = UNAUTHORIZED`, `message = Unauthorized`,
  `payload = null`. Причина остаётся только во внутренней диагностике без PII.

### Load Considerations

- `ExpectedLoad.md` не содержит чисел, поэтому пропускная способность пока не
  нормирована.
- Каждый защищённый запрос читает общую PostgreSQL-сессию. Корректность важнее
  преждевременного кеширования; потребность в read model подтверждается измерениями.
- Серии успешных запросов, auth-отказов и исключений storage обязаны возвращать
  число checked-out DB connections к исходному уровню; каждый acquire закрывается
  и на error path.

### Security Considerations

- Негативный набор включает каждый отсутствующий/неверного типа claim, чужой
  `aud`, другой `alg`, неверную подпись, точную границу `exp`, неизвестную,
  чужую и истёкшую сессию.
- Sentinel-проверка ищет JWT, refresh-токен, секрет и PII одновременно в теле
  ответа и захваченных логах всех auth-failure веток. Структурное поле credential
  имеет фиксированное значение `[REDACTED]`; сырые значения нигде не появляются.
- Недоступное хранилище сессий разрешить запрос не может: guard fail-closed.
- Для parsing, signature, claims, session mismatch/expiry и storage failure пишется
  отдельный bounded reason-code с correlation id, но без `sub`, `sid` или PII;
  happy path auth-failure сигнал не пишет.
- Каждый error response строго совпадает с разрешённой схемой и не содержит stack
  trace, SQL, имён внутренних классов или filesystem paths.

### Schema and Deployment Notes

- `expires_at` вводится expand-contract: сначала nullable additive-колонка, затем
  writers начинают её заполнять и существующие строки backfill-ятся, после чего
  включается guard; `NOT NULL` закрепляется отдельным последующим шагом.
- N-1 read/write paths обязаны работать на новой схеме. До завершения backfill
  новый reader трактует legacy `expires_at = NULL` как неактивную сессию (`401`),
  а не падает и не разрешает доступ; эта политика закрепляется migration-тестом.
- ORM и DB constraints должны закрепить FK сессии на пользователя и UTC-aware
  `expires_at`; текущую декларативную схему необходимо синхронизировать.

### Hazard Scan Record

- Scanned groups: `hz-01`, `hz-02`, `hz-03`, `hz-04`, `hz-05`, `hz-06`,
  `hz-07`, `hz-08`.
- Folded `hz-01`: numeric/expiry edge matrix и UTF-8/date serialization guards.
- Folded `hz-04`: проверяемый expand-contract `expires_at` и legacy-row policy.
- Folded `hz-05`: JSON metacharacter/injection guard.
- Folded `hz-06`: 4096-octet Authorization limit и DB pool release guard.
- Folded `hz-07`: обе expiry boundaries, failure reason-codes и fixed redaction.
- `hz-02`, `hz-03`, `hz-08`: triggers не применимы к server-side read-only GET.
- Seam synthesis: numeric expiry guard несёт hz-07; Unicode/date guard несёт
  hz-01; oversized Authorization guard несёт hz-06. Canonical write/async seams
  не активируются.

### Integration Notes

- Внешних API и сервисов нет. История самостоятельна, но JWT-контракт совместим
  с EmailCodeLogin, SessionRenewal и ADR `unified-client-auth-decision.md`.
- Выпуск, ротация и logout не реализуются здесь; guard не зависит от способа
  выпуска токена.

## Additional Context

- Пользовательские решения и полный negative matrix: `interview.md`.
- Named precedents: Story 1 EmailCodeLogin и ADR задачи 1 о едином JWT клиентов.
