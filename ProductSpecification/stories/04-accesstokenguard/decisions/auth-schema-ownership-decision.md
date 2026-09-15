# Decision: `auth.t_users` создаёт история 4; `expires_at` не переоформляется

**Date**: 2026-08-16 **Scenarios**: 1.1 (01_API), 1.1–1.3 (04_Infrastructure)

Сценарий 1.1 недостижим: `auth.t_users` не создаёт ни одна ревизия, а acceptance-сьют
вставляет строку с типом `auth.user_gender`. Одновременно `04_Infrastructure_Tests.md`
требует, чтобы `auth.t_sessions.expires_at` вводился как additive → backfill → `NOT NULL`,
но история 5 уже сделала ревизию `0001_auth_sessions`, создающую таблицу сразу с
`expires_at timestamptz NOT NULL`.

| Rejected | Why |
|----------|-----|
| Ждать EmailCodeLogin, которая по docstring `0001` должна создать `auth.t_users` | `interview.md` требует, чтобы история доставлялась самостоятельно; Tier 1 иначе не запускается вовсе |
| Переписать `0001_auth_sessions` в additive-форму (`expires_at NULL` → backfill → `NOT NULL`) | Ревизия принадлежит идущей параллельно истории 5; правка чужой миграции в общем worktree — конфликт, а сама трёхшаговая раскатка защищает строки, которых не существует: таблица создаётся этой же нерелизнутой ревизией |
| Добавить FK `auth.t_sessions.user_id → auth.t_users.id` в ревизии `0002` | Сессии пишутся с ревизии `0001`, до появления пользователей; ограничение, добавленное здесь, отвергло бы уже легальные строки и сломало бы фикстуры истории 5 |

**Chosen**: ревизия `0002_auth_users` (chained на `0001_auth_sessions`) создаёт
`auth.user_gender` и `auth.t_users` и ничего больше. `expires_at` остаётся таким, каким
его создала `0001`. Совместимость со смешанным развёртыванием обеспечивается не
миграцией, а **путём чтения**: строка с `expires_at IS NULL` отображается в `None` и
трактуется как неактивная сессия — единый `401`, неотличимый от неизвестной сессии.
Это и есть половина Infrastructure 1.1, которую невозможно добавить позже без
переработки, поэтому она заморожена сейчас.

FK и `auth.t_auth` остаются за EmailCodeLogin; она не должна пересоздавать
`auth.t_users` и `auth.user_gender`.

## Model

- `backend/adapters/storage/src/adapter_storage/migrations/versions/20260816_1500_auth_users.py`
  — `revision = "0002_auth_users"`, `down_revision = "0001_auth_sessions"`; `CREATE TYPE`
  под `IF NOT EXISTS`-проверкой в `pg_type`, `create_table(..., if_not_exists=True)`,
  поэтому повторное применение и применение поверх прерванной попытки дают то же состояние.
- `adapter_storage/models/user.py` — `UserEntity`; `gender` использует
  `Enum(..., create_type=False)`, чтобы импорт модели никогда не выпускал `CREATE TYPE`.
- `adapter_storage/mappers/active_session.py` — `ActiveSessionMapper.to_domain` возвращает
  `None` при `expires_at IS NULL`.
- `domain/auth/failure/` — отдельная причина `LEGACY_SESSION`, чтобы неприменённый
  backfill был различим в логах, оставаясь неотличимым снаружи.

## Edge Cases

| Case | Behavior |
|------|----------|
| Ревизия `0002` применена повторно | Ни enum, ни таблица не создаются заново, ошибки нет |
| Первая попытка прервалась после `CREATE TYPE` | Повтор дозакрывает создание таблицы |
| Строка сессии с `expires_at IS NULL` | Единый `401`, reason `legacy_session` |
| Внешняя БД, где `auth.t_sessions` уже существует без `expires_at` | Раскатка additive → backfill → `NOT NULL` добавляется отдельной ревизией; backfill обязан фильтровать `WHERE expires_at IS NULL` и не переписывать заполненные строки |
| Пустой scope backfill | 0 изменённых строк, constraint не устанавливается досрочно |
