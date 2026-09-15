# Stage 2 — полосы реализации (Story 1, сценарий 4.6)

Координатор ведёт эту запись как машину состояний. Работники ничего не стейджат и не коммитят;
стейджинг и коммиты выполняет только координатор по явно перечисленным путям.

## Полосы

Одна полоса — `adapter-storage`. Она выведена из архитектурной границы (реализация
`SessionIssuancePort` в `adapter_storage`), а не из числа файлов. Второй полосы нет:
usecase, domain, rest и application по контракту Stage 1 — NO_CHANGE.

| Полоса | Единица | Пути RED (тесты) | Пути GREEN (продакшн) |
|---|---|---|---|
| adapter-storage | SessionIssuance storage boundary | tests/test_session_issuance_repository.py, tests/storage_testing/statements/session_issuance.py, tests/storage_testing/statements/session_issuance_data.py (новый) | src/adapter_storage/repositories/session_issuance.py, src/adapter_storage/models/user.py, src/adapter_storage/migrations/versions/20260907_1200_auth_users_email_normalized.py (новый) |

Манифесты не пересекаются: RED пишет только под `tests/`, GREEN — только под `src/`.

## RED — наблюдён сырым

Команда: `uv run pytest backend/adapters/storage -v`.

**Предсказание (до запуска):** оба новых кейса падают на первом `assert` в
`assert_reused_the_*_user_without_creating_one` — сравнение списка `IssuedSessionRecord`.
Причина: `_find_user_by_email` делает точное `UserEntity.email == provider_id`, не находит
строку, сохранённую в другом регистре или с пробелами, и `_resolve_user` создаёт нового
пользователя: ожидается `[IssuedSessionRecord(user_id=CANDIDATE_USER_ID, ..., created_user=True)]`
вместо `[IssuedSessionRecord(user_id=<SEEDED>, ..., created_user=False)]`.

**Фактический результат:**

```
test_should_reuse_the_existing_user_when_stored_email_has_different_case FAILED
>       assert self._issued == [
            IssuedSessionRecord(user_id=MIXED_CASE_USER_ID, session_id=FIRST_SESSION_ID, created_user=False)
        ]
E       AssertionError
session_issuance.py:77: AssertionError

test_should_reuse_the_existing_user_when_stored_email_has_surrounding_whitespace FAILED
>       assert self._issued == [
            IssuedSessionRecord(user_id=WHITESPACE_USER_ID, session_id=FIRST_SESSION_ID, created_user=False)
        ]
E       AssertionError
session_issuance.py:83: AssertionError

2 failed, 6 passed in 0.70s
```

**Сравнение:** совпало точно — тот же метод, тот же первый `assert`, та же причина
(репозиторий создал кандидата вместо переиспользования). Ретроподгонки предсказания не было.

Регресс: `11 passed, 2 skipped` по всему модулю storage после того, как оба новых кейса
помечены `@pytest.mark.skip` по-методно (class-level маркер отключил бы и шесть зелёных).

Размеры файлов после RED: test_session_issuance_repository.py 68, session_issuance.py 180,
session_issuance_data.py 31 — все в пределах лимита 200.

Вынос констант в `session_issuance_data.py` сделан внутри RED-фазы намеренно: файл statements
был 157 строк и добавление двух случаев вывело бы его за лимит.

## Чекпойнт полос

<!-- lanes: storage={red:2039e9d,green:3c66d06,refactor:d53ebaa} PASS -->

## Ревью тестов (три кластера, RED-фаза)

Кластер A: 4 находки — тавтологичное given-условие, слепое пятно по направлению дубликата,
отсутствующая проверка строки сессии, недетерминированная форма кода. Кластер P: 2 находки
по check 16 (setup через `self._users.add_one` в обход usecase; инъекция `AuthDatabase` в
acceptance Statements) — обе унаследованы от шести исходных тестов, 4.6 их не вносил;
эскалированы в отчёт, не чинятся здесь. Кластер S: 7 находок, из них ключевая — шесть
почти одинаковых `assert_*`-методов.

Три находки из трёх кластеров сведены в одну правку: приватный параметризованный
`_assert_reused_without_creating(user_id, account_rows, session_row)` плюс два тонких
публичных композита. Итог: три оси проверки вместо двух, меньше дублирования, +2 строки.
Усиленный тест перепроверен на красноту — при спрятанном `src` даёт `2 failed, 11 passed`.

## GREEN

Решающая правка — `lower(btrim(email))` в поиске пользователя, функциональный уникальный
индекс `uq_t_users_email_normalized` в модели и ревизия `0005_auth_users_email_normalized`,
которая перед любым изменением сканирует коллизии и падает, а не сливает строки молча.
Атомарность по построению: alembic оборачивает ревизию в транзакцию, `CREATE INDEX
CONCURRENTLY` не используется. Проверки: storage 13 passed, backend 63 passed,
lint-imports 1 kept / 0 broken.

## Покрытие

`models/user.py` 100%, `repositories/session_issuance.py` 95%. Единственная непокрытая
строка — ранний `return None` для не-EMAIL провайдера; в `AuthProvider` есть только
`EMAIL`, тест на неё был бы вакуумным. Шаг не заводится.

## Рефакторинг

Кластер M: `upgrade()` разбит на четыре именованных шага (27 строк, четыре блока с разной
семантикой отказа). Кластер D: выражение нормализации сведено к общему `normalized_email()`
в модуле модели, обе стороны сравнения нормализуются одинаково. Дублирование SQL внутри
миграции оставлено намеренно — применённая ревизия обязана оставаться самодостаточной.

Две находки помечены NOT-A-REFACTOR и вынесены в отчёт: неявный контракт «`provider_id`
для EMAIL обязан быть продуктом `Email.of`», нигде не проверяемый в рантайме; и
необработанная гонка check-then-insert на уникальном индексе в `_resolve_user`.

## Блокер stage-3

Ревизия `0005` не накатывается на dev-базу: сканер коллизий нашёл 6 групп — остатки строк
от собственных acceptance-прогонов RED этой сессии. `alembic current` = `0004_auth_accounts`.
Санкционированного IaC-скрипта очистки тестовых данных в `infrastructure/scripts/` нет.
