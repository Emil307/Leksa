# Decision: Контракты проверки кода

**Date**: 2026-09-03 **Scenarios**: 4.1 (Tier 1), шов общий с 4.2, 4.3, 4.5, 5.x, 6.1, 7.2, 7.3

Сценарий 4.1 — первый код на стороне `verify`. Как и в 2.1, шов замораживается целиком: половина
контракта (только «найти пользователя и выдать сессию») заставила бы разморозить порт на 4.2, 5.1 и
6.1, то есть трижды. Ниже — весь шов `verify`, из которого Stage 2 реализует ровно то, что требует
сфокусированный тест 4.1.

| Rejected | Why |
|----------|-----|
| Сравнивать код Lua-скриптом внутри Redis одной операцией «сравнил и удалил» | Lua-сравнение строк не постоянно по времени и утекает через задержку ответа. Постоянное сравнение уже живёт в домене (`VerificationCode.matches`), и оно должно остаться единственным. |
| Один метод порта `verify_and_consume(challenge_id, code)` | Он потащил бы сырой код в адаптер и туда же — правило сравнения. Порт отдаёт запись, домен сравнивает. |
| Адаптер собирает `Challenge` с готовым `ChallengeSecret` | Адаптер не знает, код это, deep-link или `state`: конкретный тип секрета принадлежит стратегии. Порт отдаёт плоскую `StoredChallenge` со `secret_value: str`, секрет восстанавливает `ChallengeStrategy.restore_secret`. |
| Сервис знает, что `uniqueness_key` — это email, и ищет пользователя по нему | Тот же довод, что и в 2.1: `TG` и `OAUTH` ключуются не по почте. Сервис спрашивает у стратегии `account_for(uniqueness_key) -> ProviderAccount`, а `ProviderAccount` — это ровно пара `(provider, provider_id)` из `auth.t_auth`. |
| Три порта хранилища (`users`, `accounts`, `sessions`), которыми сервис управляет по очереди | Три вставки — одна транзакция; оркестрация тремя портами вытащила бы границу транзакции в usecase и потребовала бы утечки Unit of Work. Один порт `SessionIssuancePort.issue_session` = одна транзакция = одна граница отказа. |
| Отдельная сессионная строка на пользователя (upsert) | Сессий у пользователя много (`interview.md`); каждый успешный `verify` вставляет новую строку. Сценарий 4.5 стоит на этом. |
| Добавить методы `verify` в уже отгруженный `ChallengeStorePort` | `StartAuthChallengeService` получил бы пять методов, которых никогда не вызывает. Порты разделены: `ChallengeStorePort` (старт) и `ChallengeVerificationStorePort` (проверка); одна дистрибуция `adapter_cache` реализует оба. |
| Второй параметр у `create_auth_challenge_router` | Сломал бы отгруженную сигнатуру и её тесты. `verify` получает свой роутер `create_auth_verify_router` под тем же префиксом — так же, как уже разведены `auth_token.py` и `profile.py`. |
| Строгая Pydantic-схема (`challengeId: UUID`, `code: str`) | FastAPI вернул бы 422 вместо отгруженного конверта `{code, message, payload}` с 400. Оба поля объявлены `Any`, отвергает их домен. |
| Смонтировать `/verify` в `main.py` уже на Stage 1 | `get_verify_challenge_service()` — скелет; смонтированный роутер уронил бы `create_app()` и весь набор тестов. Монтаж принадлежит полосе композиционного корня в Stage 2. |
| Отложить `find_verification` / `remember_verification` до сценария 6.1 | Окно повтора — шаг 11 самого `verify`: запись о повторе создаётся в успешном проходе 4.1, а не когда-нибудь потом. Заморозить её позже — вторично размораживать порт. |

**Chosen**: домен владеет разбором входа, восстановлением секрета, постоянным сравнением и расчётом
сроков; usecase-сервис оркестрирует семь портов и не знает ни про Redis, ни про Postgres, ни про JWT;
Redis гасит challenge, Postgres одной транзакцией выдаёт личность и сессию, композиционный корень
подписывает токен.

## Поток `verify`

1. `ChallengeId.of(raw)` и `PresentedSecret.of(raw)` — разбор входа. Оба метод-агностичны: `ChallengeId`
   требует UUID, `PresentedSecret` — непустую строку в границе октетов. Ни длины кода, ни алфавита здесь
   нет: это знание семейства методов на коде, а не ядра.
2. `find_challenge(challenge_id)` — чтение без побочных эффектов. Оно нужно ровно для одного: узнать
   `challenge_type` и через него — стратегию, чтобы проверить **форму** предъявленного секрета до того,
   как будет потрачена попытка. Иначе «пять цифр» и «шесть символов с буквой» съедали бы попытку, а
   сценарий 3.1 требует обратного.
3. `claim_attempt(challenge_id, max_attempts)` — атомарный инкремент счётчика попыток. Он же возвращает
   свежую запись, поэтому чтение на шаге 2 не обязано быть актуальным: гонка «challenge вытеснен между
   шагами 2 и 3» разрешается сама — `claim_attempt` вернёт `missing()`, и ответ будет 401. Достижение
   `max_attempts` удаляет запись и указатель в той же операции и возвращает `exhausted_now()`.
4. `strategy.restore_secret(claim.challenge.secret_value).matches(presented.value)` — единственное
   сравнение кода во всём продукте, постоянное по времени по всей длине (`VerificationCode.matches`,
   отгружено в 2.1).
5. `redeem_challenge(challenge_id)` — атомарное «удали, если есть», возвращает `True` только победителю.
   Проигравший (сценарии 6.1 и 7.2) идёт за `find_verification`, а не получает отказ.
6. `issue_session(SessionIssuanceRequest)` — одна транзакция Postgres: найти пользователя по
   `(provider, provider_id)`, при отсутствии создать (`name=''`), обеспечить строку `t_auth`, вставить
   строку `t_sessions`. Возвращает `IssuedSessionRecord(user_id, session_id, created_user)`.
7. `remember_verification(ChallengeVerification, ttl_seconds)` — запись о повторе под погашенным
   `challengeId`.
8. `access_tokens.issue(AccessTokenClaims(...))` — подпись JWT.

**Гашение раньше базы — осознанный размен**, уже объявленный в `01_EmailCodeLogin.md` и в
`auth_challenge_verify.yaml`: упавшая транзакция тратит код. Порядок не переставляется, потому что
обратный порядок допускает две сессии по одному коду.

## Model

**domain.auth.challenge** — ядро

- `ChallengeId.of(raw: object)` — разбор идентификатора из тела запроса. Не строка, не UUID, `null`,
  отсутствие — `ValidationException` (400), а не 422 от FastAPI.
- `PresentedSecret.of(raw: object)` — предъявленный секрет: строка, непустая, в границе
  `MAX_PRESENTED_SECRET_OCTETS`. `__repr__`/`__str__` затёрты — предъявленный код не попадает ни в лог,
  ни в трассировку. Число JSON (`123456` без кавычек) отвергается здесь, а не приводится к строке молча.
- `ChallengeVerification(challenge_id, user_id, session_id)` — то, что живёт в окне повтора. Ни кода, ни
  refresh-токена в ней нет: повтор перевыдаёт `refreshToken` из строки сессии, а не из кеша.
- `ChallengePolicy.replay_ttl_seconds(now, expires_at)` — окно повтора представлено **сроком жизни
  записи**, а не полем `created_at` со сравнением на чтении: `min(replay_window_seconds, секунды до
  expires_at)`, целыми секундами. Redis сам выкидывает запись, и «повтор после окна» становится
  неотличим от «challenge никогда не было» — ровно то, чего требует сценарий 5.4. Запись о повторе не
  живёт дольше самого кода.
- `ChallengeStrategy` получает два новых метода: `restore_secret(value)` и `account_for(uniqueness_key)`.
  Оба обязательны: тип без стратегии по-прежнему не имеет ветки по умолчанию.

**domain.auth.user**

- `AuthProvider` — перечисление провайдеров личности (`EMAIL = "email"`), значение колонки
  `auth.t_auth.provider`. Живёт в ядре по тому же основанию, что и `ChallengeType`: это не деталь метода,
  а способ, которым личность записана.
- `ProviderAccount(provider, provider_id)` — учётная запись провайдера. Для `EMAIL_CODE`
  `provider_id` — нормализованный email, поэтому «Bob@Example.COM» и «bob@example.com» — одна личность
  (сценарий 8.4) без единой дополнительной строки кода: нормализация уже сделана `Email.of` на `start` и
  лежит в `uniqueness_key` записи challenge.

**usecase**

- `ChallengeVerificationStorePort` — `find_challenge`, `claim_attempt`, `redeem_challenge`,
  `remember_verification`, `find_verification`. `StoredChallenge` — плоская проекция записи со
  `secret_value: str` и затёртым `__repr__`; `ChallengeClaim` различает «нет записи» и «попытки только
  что исчерпаны», потому что наружу оба дают один и тот же 401, а в лог — разные причины.
- `SessionIssuancePort.issue_session(SessionIssuanceRequest) -> IssuedSessionRecord`. Идентификаторы
  (`candidate_user_id`, `session_id`) генерируются в usecase через отгруженный `IdGeneratorPort`, как и в
  `start`: политика идентификаторов не переезжает в адаптер. `candidate_user_id` используется только
  если пользователя ещё нет; при существующем пользователе он просто выбрасывается, и возвращённый
  `created_user=False` — то самое «нового пользователя не создаётся» из сценария 4.1.
- `VerifyAuthChallengeService.verify(VerifyChallengeRequest) -> VerifiedSession`. `VerifiedSession` и
  `VerifyChallengeRequest` затирают токены и код в `__repr__`/`__str__`, как отгруженная
  `RotatedSessionTokens`.

**adapters**

- `adapter_cache`: ключи вынесены в `keys.py` (`RECORD_KEY`, `POINTER_KEY`, `COOLDOWN_KEY` и новый
  `VERIFICATION_KEY`), потому что теперь их читают два класса. `RedisChallengeVerificationStore` —
  вторая точка входа той же дистрибуции; `RedisChallengeStore` не растёт и остаётся в границе 200 строк.
  Все ключи по-прежнему читаются напрямую, перебора ключей нет.
- `adapter_storage`: `AuthAccountEntity` (`auth.t_auth`) с уникальностью по паре
  `(provider, provider_id)` — так, как требует `interview.md`, а не по одному `provider_id`; FK на
  `t_users` с `ON DELETE CASCADE`. `SessionIssuanceRepository` — весь шаг 6 в одной транзакции.
- `adapter_rest`: `ChallengeVerifyRequest` (`extra="ignore"`, оба поля `Any`), `ChallengeVerifyResponse`
  (`extra="forbid"`, ровно `user.id` и `session {id, refreshToken, accessToken}`; `userId` внутри
  `session` не дублируется). Роутер `create_auth_verify_router` под тем же префиксом `/api/v1/auth/challenge`.
- **JWT подписывается в композиционном корне** — `application/security/jwt_access_token_issuer.py`,
  реализация отгруженного `AccessTokenIssuerPort`. Секрет приходит настройкой `JWT_SECRET`, у которой нет
  рабочего значения по умолчанию в коде; значение для локальной разработки выдаёт `setup-ports.sh`.
  Четвёртой дистрибуции ради подписи не заводится — по тому же основанию, что часы и генератор
  идентификаторов в 2.1.

## Edge Cases

| Case | Behavior |
|------|----------|
| `challengeId` отсутствует, `null`, не UUID или не строка | 400 `VALIDATION_FAILED`, ни одного обращения к хранилищу, попытка не тратится |
| `code` не строка, пустой, вне границы октетов | 400 `VALIDATION_FAILED` до `claim_attempt` |
| `code` — строка неверной формы (пять цифр, буква, арабо-индийские цифры) | 400 `VALIDATION_FAILED`: форму проверяет стратегия после `find_challenge`, попытка не тратится |
| Код неверен | Попытка потрачена в `claim_attempt`, 401 `UNAUTHORIZED`, остаток попыток наружу не отдаётся |
| Попытки исчерпаны этой проверкой | Запись и указатель удалены в той же атомарной операции; следующий запрос неотличим от «никогда не было» |
| Неизвестный / истёкший / вытесненный `challengeId` | `claim_attempt` возвращает `missing()`, ответ ровно тот же 401 с тем же телом — эндпоинт не годится для разведки |
| `redeem_challenge` вернул `False` | Гонку выиграл другой запрос: ответ берётся из `find_verification`, а не отказ (сценарии 6.1 и 7.2) |
| Транзакция базы упала | 503 `UNAVAILABLE` без деталей; ни `t_users`, ни `t_auth`, ни `t_sessions`, ни записи о повторе. Код при этом уже потрачен — размен объявлен |
| Пользователь есть, строки `t_auth` с `provider='email'` нет | `issue_session` создаёт ровно её, пользователя не дублирует (`created_user=False`) |
| Повтор после окна | Запись о повторе истекла по TTL — ответ неотличим от истёкшего challenge |

## Открытые расхождения (не чинятся здесь)

- Отгруженный обработчик `UnauthorizedException` отдаёт фиксированное тело
  `{"code": "UNAUTHORIZED", "message": "Unauthorized", "payload": null}`. Требование `endpoints.md`
  «`UNAUTHORIZED` различается сообщением» через него недостижимо, а требование `auth_challenge_verify.yaml`
  «`payload` — объект» нарушено (`null`, а не `{}`). Для 4.1 это не наблюдаемо. Причина отказа
  по-прежнему едет в лог через отгруженный `unauthorized(reason)`. Разбирается на сценариях 5.1/5.4,
  которые эти ответы и утверждают.
- `AUTH_CHALLENGE_REPLAY_WINDOW_SECONDS` в коде имел значение по умолчанию 30 при 60 в спецификации.
  Умолчание исправлено на 60, и переменная выведена в `.env.example`/`setup-ports.sh` — окно повтора
  перестаёт быть числом, зашитым в код.
