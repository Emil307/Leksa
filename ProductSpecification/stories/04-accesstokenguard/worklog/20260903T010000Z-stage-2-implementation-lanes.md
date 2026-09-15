# 1.1 Пользователь с действующей сессией получает всю свою запись — stage-2 implementation lanes

Started: 2026-09-03T01:00:00Z

Outcome: completed

- Change: четыре непересекающиеся линии доведены от RED до GREEN; тесты сценария включены.
- Tests: backend 56 passed, 0 failed, 0 skipped (было 14 passed, 42 skipped).
- Architecture: import-linter 1 kept, 0 broken. ruff check backend — clean.
- Coverage (focus): authenticate_request 100%, read_user_profile 100%, active_session 100%,
  user 100%, failure/* 100%; bearer_credential 82% и verified_access_token 84% — непокрытое
  принадлежит Security 1.1/2.2/2.3 из Tier 2 этой же истории.

## Lane checkpoints

- usecase — RED 14, GREEN 16 passed. Statements разделены на auth.py (when/assert) и
  auth_arrangements.py (given), иначе файл превышал 200 строк.
- adapter-storage — RED 11, GREEN 12 кейсов. Исправлены два дефекта миграции 0002_auth_users.
- adapter-rest — RED 6 + 2 ALREADY_GREEN, GREEN 8 passed. rest_testing разбит на четыре модуля.
- adapter-application-security — RED 10, GREEN 12 passed.

## Manifest amendments

- usecase_testing/statements/auth_data.py, auth_arrangements.py — разделение по лимиту 200 строк.
- storage_testing/auth_repositories.py, migration_db.py, auth_schema.py, auth_assertions.py,
  tests/conftest.py — вынос драйверов и ассертов из тест-классов.
- rest_testing/profile_data.py, profile_fakes.py, profile_statements.py, exception_handlers.py.
- application_testing/ — новый пакет поддержки; tests уже в pythonpath, конфиг не менялся.
- Отказ по вне-доменному gender перенесён из mappers/user.py в UserRepository.find_by_id:
  SQLAlchemy декодирует enum при выборке строки, до маппера, и бросает LookupError внутри
  get_one. Наблюдаемое поведение (единый 401, не 500) не изменилось. См.
  decisions/access-token-claims-contract-decision.md.

## Cross-lane contracts settled by the coordinator

- LEGACY_SESSION: mapper возвращает None при expires_at IS NULL; repository на такой строке
  бросает unauthorized(LEGACY_SESSION). Отсутствующая строка по-прежнему None. Так причина
  различима в логах и неотличима снаружи — обе половины edge-case ADR выполнены.
- isSuperuser: на минимально заполненной строке False, не None — колонка несёт server_default.
  REST-фикстура фиксировала недостижимую ветку и исправлена.

## Findings recorded, not fixed

- Gender.parse не имеет ни одного вызывающего после переноса отказа в репозиторий — мёртвый код.
  Это замороженная поверхность Stage 1, поэтому удаление отложено на разбор Stage 3.
- Подготовка состояния в AuthStatements пишет напрямую через фейки портов: в скоупе истории 4
  нет юзкейса, выдающего сессию или создающего аккаунт. Разрыв закрывается EmailCodeLogin.
- .venv/bin/lint-imports и .venv/bin/alembic несут мёртвый shebang на чужой воркtree; рабочие
  пути — python -m alembic и importlinter.use_cases.lint_imports. python -m importlinter.cli
  молча возвращает rc=0 ничего не проверив.
- Скипы снимались только координатором; ни один воркер не стейджил и не коммитил.

<!-- lanes: usecase=PASS; adapter-storage=PASS; adapter-rest=PASS; adapter-application-security=PASS -->
