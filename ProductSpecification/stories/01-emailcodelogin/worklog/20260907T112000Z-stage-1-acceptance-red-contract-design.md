# 4.6 Пользователь, чей email записан в базе в другом регистре, не получает второго аккаунта — stage-1 acceptance RED + contract design

Started: 2026-09-07T11:00:00Z

Outcome: completed

Блок несёт `<!-- review-origin: boundary -->` — закрывающая граница сценария
пропускает `agent-review` и `premortem` (глубина ревью ограничена одним поколением).

## Разделение владения полосами

| Полоса | Пишет | Не трогает |
|---|---|---|
| acceptance RED | `acceptance/tests/backend/auth/test_challenge_verify_stored_spelling_acceptance.py`, `acceptance/statements/challenge_verify_stored_spelling_statements.py`, `acceptance/statements/auth_database.py`, `acceptance/conftest.py` | `backend/**`, `ProductSpecification/**` |
| contract design | `ProductSpecification/stories/01-emailcodelogin/decisions/challenge-verify-legacy-email-case-decision.md` | `acceptance/**`, `backend/**` |

Манифесты непересекающиеся, ни одна полоса не зависела от нового вывода другой.

## Полоса acceptance RED

Цели: два случая из таблицы написаний сценария — разный регистр и окружающие пробелы.

**Predicted failure.** Оба случая: `verify` отвечает 200, но с идентификатором
*нового* пользователя, а не засеянного, потому что поиск в хранилище сравнивает
хранимый email дословно с нормализованным адресом; падает
`assert_session_belongs_to_the_stored_user`.

**Actual failure.**
```
AssertionError: verify must answer with the user already stored as
'Learner-7C47Ac895Cb5@Uwords-Acceptance.Local' — '8931aede-0fa3-4a4c-b5dc-766ea23ce2b5'
— got 'b70a76bf-a85c-4695-aa83-f81370c25b47'
```
```
AssertionError: verify must answer with the user already stored as
' learner-9b1622f100b6@uwords-acceptance.local ' — 'e7bf64ce-1f16-441b-b135-6c60070c689e'
— got '22e4fdaf-f69b-4f7d-9285-319095aef522'
```

**Comparison.** Совпало по всем полям в обоих случаях: тот же тест, то же
утверждение, тот же статус 200, то же расхождение идентификаторов. Ни один случай
не оказался уже зелёным.

Прогон до маркера: `2 failed, 6 deselected`. Полный прогон после маркера:
**4 passed, 4 skipped, 0 failed**.

## Дефект, который делает сценарий красным

`backend/adapters/storage/src/adapter_storage/repositories/session_issuance.py:55` —
`select(UserEntity.id).where(UserEntity.email == request.account.provider_id)`.
`provider_id` всегда нормализован (`domain/auth/user/email.py:20`: `strip` + NFC +
`lower`), хранимая колонка — нет, а `t_users.email` объявлен обычным
регистрозависимым `unique=True`
(`migrations/versions/20260816_1500_auth_users.py:55`) — проверено отдельно, дубль
действительно создаётся.

## Клауза за клаузой

| Клауза Gherkin | Чем доказывается |
|---|---|
| ответ несёт идентификатор того самого заведённого пользователя | `assert_session_belongs_to_the_stored_user` — строгое `==` с реальным засеянным uuid |
| второго пользователя с этим адресом не появляется | `assert_no_second_user_owns_the_address_in_any_spelling` — нормализующий запрос по `t_users`, ловит дубль, записанный под нормализованным адресом |
| учётная запись провайдера «email» указывает на заведённого пользователя | `assert_email_account_points_at_the_stored_user` — от пользователя к аккаунтам **и** встречно от адреса к держателям `t_auth` |

## Полоса contract design

`NO_CHANGE` в `backend/**` на уровне контрактов: домен, use case, порты и REST не
меняются; весь сценарий лежит на границе storage-адаптера, поэтому Stage 2 — ровно
одна полоса без межполосных зависимостей. Решение:
`decisions/challenge-verify-legacy-email-case-decision.md` (140 строк).

Baseline на HEAD: `pytest backend` — **61 passed**; `lint-imports` — 138 файлов,
212 зависимостей, контракт KEPT, **1 kept / 0 broken**.

Проверено полосой отдельно: `t_auth.provider_id` вне объёма 4.6 (0 из 31 строки
ненормализованы; `t_auth` создана ревизией `0004` внутри этой же истории), и
сценарий 8.4 второго уровня не поглощён.

## Детекторы тестов (три кластера параллельно)

**Кластер P** — чисто по 11 структурным проверкам. Две находки уровня эскалации, не
локальной правки: посев идёт через `store_user` прямо в `auth.t_users` (неустранимо
в принципе — сценарию нужно написание, которого API физически не может создать), и
`AuthDatabase`, инжектируемый в Statements, — устоявшаяся идиома всего модуля.

**Кластер S** — 7 находок. Главная: предусловие проверялось *нормализующим*
запросом, то есть прошло бы одинаково и при сохранённом дословном написании, и при
приведённом — единственная посылка, на которой стоит сценарий, не утверждалась нигде.

**Кластер A** — 4 находки: то же тавтологическое предусловие, слепая зона на вторую
строку `t_auth`, отсутствие утверждения о самой сессии, слабая форма кода.

### Применено

1. Предусловие переписано: до посева — «адресом не владеет никто ни в одном
   написании»; после посева — дословная проверка `users_with_email(stored_email) ==
   [(id, name)]` и `users_with_email(requested_email) == []`. Прогон подтвердил, что
   посев сегодня невакуумен: строка сохранила `Learner-7C47Ac895Cb5@…` буквально.
2. Встречная проверка `t_auth` по адресу — новый параметризованный запрос
   `email_identity_user_ids_ignoring_case_and_spaces`. Закрывает дубль идентичности,
   который прежние утверждения не видели.
3. Утверждение о сессии: `session_ids_of_user(user_id) == [session.session_id]`.
4. Написание в базе приведено к смешанному регистру таблицы сценария
   (`Ivan@Uwords.App`) вместо прежнего `upper()`.
5. Форма кода: `code.isdigit()` вместо `is not None`.
6. Фикстура переехала в корневой `acceptance/conftest.py` к обеим сёстрам.

Честно: встречная проверка `t_auth` в RED отдельно не проявляется — в том же методе
раньше срабатывает утверждение о списке аккаунтов. Несущей она становится в GREEN.

### Отложено в `/refactor` этой же единицы

Четыре находки кластера S на дублирование между Statements: третий клон конструктора
`UserRecord`, трижды скопированный блок «запросить код и достать из outbox»,
задвоенная `EMAIL_PROVIDER`, `verify_code`, смешивающий действие и утверждение.

## Веер опасностей hz-01..hz-08 (восемь сканов параллельно)

| Группа | Вердикт |
|---|---|
| hz-01 текст и представление | GAPS 4 |
| hz-02 повторный прогон и атомарность | GAPS 3 |
| hz-03 одновременность | GAPS 2 |
| hz-04 жизненный цикл данных и схема | GAPS 6 |
| hz-05 граница запроса | GAPS 2 |
| hz-06 масштаб и ресурсы | GAPS 4 |
| hz-07 время, эксплуатация, раскрытие | GAPS 4 |
| hz-08 клиент/фронтенд | CLEAR — снят как блок «вне высоты» |

Подавляющее большинство GAP-ов адресовано ревизии `0005`, то есть работе Stage 2, и
существующим сценариям Tier 2 (7.3, 8.4, 4.5, 1.1, 1.3, 1.4, 2.1, 3.1, 6.1).
Заявлено 20 швов, сведены в `scratchpad/seams-4.6.md`.

Четыре группы независимо указали на одну поверхность — `t_auth.provider_id`,
оставленный на точном сравнении (hz-01 GAP 3, hz-03 наблюдение, hz-04 GAP 6,
hz-05 GAP 2).

## Синтез швов

**Ни один шов не вынуждает менять Gherkin-клаузы или таблицу написаний 4.6.**
Из 21 сведённого шва 7 закрыты уже существующими сценариями (7.3 — атомарность и
отсутствие имени ограничения в ответе; 8.4 — NFC/NFD и турецкая I), остальные
открыты и все лежат вне Tier 1.

Одиннадцать открытых швов (1, 3, 5, 7, 9, 12, 15, 16, 17, 19, 20) — это один и тот
же непокрытый угол: **у ревизии `0005` нет ни одного именованного стража** на
атомарность, повторный прогон, поведение при коллизии нормализованных ключей и
совместимость со смешанной выкаткой. План Stage 2 описывает это прозой, но ни один
файл `tests/*.md` не заводит сценарий. Закрывается одним Tier 2 стражем миграции.

Отдельно открыты: шов 2 — гонка **разных** написаний одного адреса (7.3 покрывает
только одинаковое написание); шов 18 — зависимость `lower(btrim())` от коллации
базы, не зафиксированной ни в одном окружении.

Шов 21 — `t_auth.provider_id`, на который независимо указали четыре группы, — это
**один** страж, а не четыре, и он Tier 2: последствие меньше (дубль строки-аккаунта
у существующего пользователя, не дубль личности).

Ни один из этих guard-ов не заводится в `progress.md` в рамках 4.6: блок несёт
`review-origin: boundary`, и находки ревью не порождают следующее поколение.

<!-- stage-2-plan:
adapter-storage: unit=SessionIssuance storage boundary (adapter_storage implementation of SessionIssuancePort);
writes=[
  backend/adapters/storage/src/adapter_storage/repositories/session_issuance.py: _find_user_by_email matches func.lower(func.btrim(UserEntity.email)) against the normalized provider_id, scalar_one_or_none preserved,
  backend/adapters/storage/src/adapter_storage/models/user.py: email drops unique=True, __table_args__ declares unique functional Index uq_t_users_email_normalized on lower(btrim(email)),
  backend/adapters/storage/src/adapter_storage/migrations/versions/20260907_1200_auth_users_email_normalized.py: NEW revision 0005_auth_users_email_normalized down_revision 0004_auth_accounts - guarded drop of the UNIQUE constraint over exactly (email), UPDATE email=lower(btrim(email)) only where it differs, abort with a counted error listing every colliding group before any rewrite, create unique functional index, guarded downgrade,
  backend/adapters/storage/tests/test_session_issuance_repository.py: two cases - stored mixed case and stored surrounding whitespace both reuse the seeded user,
  backend/adapters/storage/tests/storage_testing/statements/session_issuance.py: seeding statement for a stored spelling plus assertion that the issued record carries the seeded user id, no second user row exists and the email account points at the seeded user,
  backend/adapters/storage/tests/storage_testing/statements/session_issuance_data.py: NEW - constants extracted from the statements file plus the stored-spelling constants
];
frozen-surfaces=[
  SessionIssuancePort.issue_session(SessionIssuanceRequest) -> IssuedSessionRecord,
  SessionIssuanceRequest(account, candidate_user_id, session_id, refresh_token, created_at, expires_at),
  IssuedSessionRecord(user_id, session_id, created_user),
  ProviderAccount(provider, provider_id), Email.of(raw),
  VerifyAuthChallengeService.verify(VerifyChallengeRequest) -> VerifiedSession,
  SessionIssuanceMapper.build_user_dict / build_account_dict / build_session_dict and the columns they write,
  SessionIssuanceRepository.issue_session / _link_user / _find_linked_user_id / _resolve_user,
  AuthAccountEntity and index uq_t_auth_provider_provider_id,
  UserEntity column names and types (only the uniqueness declaration on email changes),
  alembic revisions 0001_auth_sessions .. 0004_auth_accounts,
  ChallengeVerifyResponse,
  acceptance/** (owned by the acceptance lane)
]
-->
