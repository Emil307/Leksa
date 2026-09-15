# 4.2 Неизвестный email регистрируется при верном коде и получает сессию — stage-1 acceptance RED + contract design

Started: 2026-09-07T10:11:00Z

Outcome: PASS — **ALREADY_GREEN**. Приёмка написана и сразу зелёная; продакшен-код 4.2 уже
поставлен вместе со Stage 2 сценария 4.1. Обе полосы отработали параллельно на непересекающихся
манифестах, ни одна не трогала `progress.md` и worklog.

## Владение (объявлено до диспетча)

| полоса | манифест |
|---|---|
| acceptance RED | `acceptance/**` |
| contract design | `backend/**`, `ProductSpecification/stories/01-emailcodelogin/decisions/**` |

Пересечений нет; ни одна полоса не зависела от нового выхода другой.

## Полоса acceptance RED — коммит `d58f98b`

Предсказание до прогона: «все четыре кейса проходят — ветка авторегистрации уже реализована».
Факт: 4/4 PASSED. Сравнение: совпало во всех четырёх ячейках.

Файлы: `acceptance/tests/backend/auth/test_challenge_verify_registration_acceptance.py` (56 строк,
класс `TestChallengeVerifyRegistrationAcceptance`, четыре кейса по одному на каждое «Тогда»),
`acceptance/statements/challenge_verify_registration_statements.py` (99),
`acceptance/statements/auth_database.py` (100 → 148), `acceptance/conftest.py` (99).

Кейсы закоммичены **включёнными**, без `@pytest.mark.skip` — маркер вешать не на что, красной фазы
не было. Прогон всего набора: 7 passed, 2 skipped; оба skip принадлежат историям 4 и 5 и не тронуты.

Два решения полосы, которые стоит помнить:

- Код запрашивается в **денормализованном** написании (верхний регистр, окружающие пробелы), иначе
  утверждение «для нормализованного адреса» было бы тавтологией.
- «Ни строки профиля, ни строки онбординга» утверждается через `information_schema`: новый
  `user_id` обязан встречаться ровно в `auth.t_auth` и `auth.t_sessions` и ни в одной другой базовой
  таблице с колонкой `user_id`. Прямой `SELECT` по `learner.t_profiles` дал бы `UndefinedTableError`
  (таблицы есть только в `docs/db-schema.sql`), а guard на существование таблицы сделал бы
  утверждение пустым.
- Проверка на невырожденность: четыре мутации продакшен-кода, каждая роняет своё утверждение;
  файл восстановлен побайтово.

## Полоса contract design — коммит `70c5fb4`, под `backend/` NO_CHANGE

Шов `verify` заморожен целиком в 4.1, и его Stage 2 реализовала ветку авторегистрации вместе с
веткой существующего пользователя — обе в одной транзакции `SessionIssuancePort.issue_session`.
Разбор по «Тогда» с доказательствами:

| «Тогда» | где уже выполнено |
|---|---|
| ровно один пользователь с пустым именем | `repositories/session_issuance.py:44-50` (единственная вставка `UserEntity` на `:49`, достижима только при `_find_user_by_email() is None`) + `mappers/session_issuance.py:11` (`"name": ""`) |
| ровно одна учётная запись «email» для нормализованного адреса | `repositories/session_issuance.py:30-32` (единственная вставка `AuthAccountEntity`, достижима только при `_find_linked_user_id() is None`) + `mappers/session_issuance.py:22-23`; цепочка нормализации от `domain/auth/user/email.py:20` (strip + NFC + lower) через ключ уникальности в оба поля идентичности |
| ровно одна сессия | `repositories/session_issuance.py:21-23` — одна вставка на вызов, та же транзакция |
| ни строки профиля, ни строки онбординга | по построению: в `models/` только `user`, `auth_account`, `session`, `notification_outbox`; ни одна из четырёх миграций не заводит схему `learner`; grep по `adapter_storage` на `learner|t_profiles|onboarding|profile` пуст |

Защита от второй строки: `uq_t_auth_provider_provider_id` (`models/auth_account.py:18`) и
`t_users.email UNIQUE` (`models/user.py:33`).

Решение записано в `decisions/challenge-verify-registration-decision.md` (95 строк).

## Adapter discovery

Порты: `ChallengeVerificationStorePort` → `adapter_cache/verification_store.py` `[S]`;
`SessionIssuancePort` → `adapter_storage/repositories/session_issuance.py` `[S]`;
`RefreshTokenGeneratorPort`, `AccessTokenIssuerPort`, `ClockPort`, `IdGeneratorPort` →
композиционный корень `[S]` (`application/wiring.py:83`, `application/main.py:36`).
Исключения → HTTP: `ValidationException` → 400, `UnauthorizedException` → 401 уже зарегистрированы;
успешный путь 4.2 исключений не бросает. Форма ответа `ChallengeVerifyResponse` не меняется.
Отсутствующих адаптеров нет, новых портов нет.

## Скан опасностей и сведение швов

Все восемь групп hz-01..hz-08 отработали; `hazard-synthesis-agent` вернул 12 швов,
**2 OPEN, 0 требующих изменения Tier 1-дизайна 4.2**.

Закрыты существующими сценариями Tier 2: S1, S10 → 7.3; S2 → 8.4; S5 → 7.2; S12 → 6.1.
Закрыт собственным текстом 4.2 (работы нет): S4. Вне истории (`01_API_Tests.md:14`): S6, S7, S8, S9.

Открыты, владельца в плане нет:

1. **S3 — запись challenge с ненормализованным ключом.** Нормализация делается один раз на `start`;
   на `verify` значение из Redis принимается на веру, и запись прежней версии кода дословно уходит
   в `t_auth.provider_id` и `t_users.email`, порождая вторую личность, которую уникальные индексы
   не остановят. Страж — повторный `Email.of` в `EmailCodeChallengeStrategy.account_for`. Ни 8.4,
   ни 4.6 сюда не дотягиваются: там оба адреса проходят через `start`. Граница истории выносит
   *нечитаемую* запись, а эта читается прекрасно — она просто ненормализована.
2. **S11 — неограниченный рост `t_sessions`.** Строки с прошедшим `expires_at` никто не удаляет —
   ни репозитория, ни задачи уборки. Страж — удаление просроченных сессий. 4.5 говорит про новую
   сессию на повторный вход, но не про судьбу старой; к границе истории не сводится: это не отказ
   хранилища, а отсутствующая операция жизненного цикла.

Пограничная заметка синтеза: мотивировка «без единой дополнительной строки кода» в
`challenge-verify-contracts-decision.md` верна только для записей, написанных текущей версией кода.
Ничего не правилось — это вход для решения пользователя, не самостоятельная правка.

## Базовые проверки на HEAD (свежие, полосой design)

`lint-imports`: Contracts 1 kept, 0 broken (138 файлов, 212 зависимостей).
`pytest backend -q`: 59 passed.

## Предложение по Stage 2

Ни одно из четырёх «Тогда» не требует новой строки продакшен-кода, поэтому фабриковать
`<!-- stage-2-plan -->` не из чего. По правилу ALREADY_GREEN шаблона `parallel-backend-stages.md`
`stage-2 implementation lanes` помечается `[S]` со ссылкой на эту запись, и сценарий уходит сразу
в Stage 3 — проверку зелёного набора и независимое ревью диапазона `d58f98b..70c5fb4`.
