# 2.1 Запрос кода возвращает challenge и кладёт в очередь готовую заявку — stage-3 acceptance GREEN + review

Started: 2026-09-03T03:00:00Z

Outcome: PASS — acceptance зелёный, оба ревью вернули CONCERNS, SAFE-находки применены

## Acceptance GREEN

Снят только маркер `@pytest.mark.skip` (и осиротевшие `RED_REASON` + `import pytest`) с
`acceptance/tests/backend/auth/test_challenge_start_acceptance.py`. Продукционный код не тронут.

Первый прогон дал не поведенческий отказ, а два блокера окружения, оба вне манифестов Stage 2:

1. **Ревизия `0002_auth_users` не проходила ни на одной базе.** `sa.Enum` молча проглатывает
   `create_type=False` — флаг понимает только `sqlalchemy.dialects.postgresql.ENUM`, — поэтому
   `op.create_table` выпускал второй `CREATE TYPE` сразу после охраняемого `DO $$`-блока и
   `alembic upgrade head` падал с `DuplicateObjectError`. Дефект унаследован от истории 0002 и
   блокировал весь acceptance-набор репозитория. Исправлен в `542d587`.
2. **Имя переменной TTL расходилось.** Statements читал `CHALLENGE_TTL_SECONDS`, а `ChallengeSettings`
   несёт `env_prefix="AUTH_CHALLENGE_"`. Ни одного из имён не было ни в `.env`, ни в генераторе.
   Это же зафиксировала находка 1 agent-review как SAFE; применено в `735af43`.

После этого: `acceptance` 2 passed, 2 skipped (два skip — сценарии историй 4 и 5, не наши).

## Вердикты ревью

| проход | вердикт | находки |
|---|---|---|
| agent-review | CONCERNS | 1 HIGH SAFE, 1 MEDIUM NEEDS_CYCLE, 4 LOW (2 SAFE, 2 NO_FIX) |
| premortem | CONCERNS | 1 high NEEDS_CYCLE, 3 NO_FIX (границы истории) |

### Применено (SAFE)

- **agent-review 1 (HIGH)** — расхождение имени переменной TTL. `735af43`.
- **agent-review 3 (LOW)** — `assert_queued_code_is_the_issued_challenge_secret` проверял только
  длину запрошенного кода, хотя имя обещает равенство кода в заявке и кода в challenge. Добавлено
  прямое сравнение `queue.messages[0].variables["code"]` с секретом из журнала `SWAP_CHALLENGE`.
- **agent-review 6 (LOW)** — Statements генератора кода мутировал `system.secrets.randbelow`
  вручную с откатом в teardown-фикстуре. Переведено на `monkeypatch.setattr`, ручной откат удалён.

### Отклонено (NO_FIX), с причиной

- **agent-review 4** — единственность строки outbox на уровне storage проверяется фейком, а не
  PRIMARY KEY реальной БД. Настоящая проверка принадлежит интеграционной категории.
- **agent-review 5 / premortem 2** — отказ компенсации `discard_started_challenge` уносит
  подготовленный конверт 503. `01_API_Tests.md` и `04_Infrastructure_Tests.md` явно выносят
  отказы хранилищ в отдельную историю. Формулировка охраны для неё: «отказ компенсации не
  понижает 503 UNAVAILABLE до 500 и не меняет конверт ошибки».
- **premortem 3** — нет ограничителя рассылки по источнику: `start` не аутентифицирован, а кулдаун
  считается по ключу уникальности, так что тысяча адресов даёт тысячу писем. Это не осознанный
  non-goal, а пробел, но охрана — новое продуктовое поведение без обязательства в 2.1. Нужен
  сценарий уровня истории.
- **premortem 4** — код в открытом виде живёт в `notifications.t_outbox` дольше challenge. Чистка
  очереди вынесена `04_Infrastructure_Tests.md` в историю планировщика.

## Допущенное предложение цикла (ожидает решения пользователя)

Оба прохода независимо назвали одно и то же: **отказ `swap_challenge` проглатывается**.

`SWAP_CHALLENGE_TEMPLATE` возвращает `0`, когда сохранённая запись новее входящей
(`adapter_cache/scripts.py:18`), но `RedisChallengeStore.swap_challenge` результат `eval` не читает,
а порт объявлен `-> None`. Сервис после отказа всё равно кладёт заявку в outbox и отвечает 200 —
пользователь получает письмо с кодом, которого нет в Redis, и `challengeId`, по которому `verify`
всегда даст 401. Нарушено уже зафиксированное обязательство 2.1 («код в заявке — тот же, который
сохранён в challenge», `01_API_Tests.md` §2.1) и ADR `challenge-start-contracts-decision.md`
(«заявка уезжает строго после того, как challenge сохранён»). Производители в проде: расхождение
часов между инстансами (`created_at` берётся из локальных часов, а бэкенд многоинстансный) и
задержавшийся запрос, переживший кулдаун. Одновременность не требуется, так что сценарий 7.1 это
не закрывает.

Направление обоих проходов совпадает: сделать отказ представимым — `swap_challenge` возвращает
исход обмена, сервис при отказе не ставит заявку и отвечает отказом. **Расходятся в коде ответа**:
premortem предлагает 503 `UNAVAILABLE` без деталей (та же терминальная семантика, что у отказа
очереди), agent-review — 409 `CONFLICT` (живёт более новый challenge того же адресата). Это
расширение замороженного контракта порта, поэтому цикл, а не правка на месте, и выбор кода ответа —
решение пользователя.

## Проверки после всех правок

`backend` 36 passed; `acceptance` 2 passed, 2 skipped; `ruff check backend acceptance` чисто;
`lint-imports` 1 contract kept / 0 broken; ни один файл не превышает 200 строк.
