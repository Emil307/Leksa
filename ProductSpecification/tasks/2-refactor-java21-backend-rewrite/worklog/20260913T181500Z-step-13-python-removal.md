# Step 13: удаление Python-бэкенда

Started: 2026-09-13T18:15:00Z

Outcome: completed

## Чекбокс 1: одним коммитом удалить Python-бэкенд

- Change: `git rm` 237 Python-файлов: `backend/*/src/{domain,usecase,adapter_*,application}`,
  `backend/*/tests`, семь module-level `pyproject.toml`, `backend/adapters/storage/alembic.ini`
  вместе с пятью Alembic-ревизиями, `.importlinter`, `requirements.txt`, `requirements-dev.txt`.
- Игнорируемые артефакты (`*.egg-info`, `__pycache__`, `htmlcov`, `coverage.xml`) вычищены
  `git clean -X` только под `backend/`; `uv.lock` (неотслеживаемый) не тронут.
- Проверено: ни один скрипт под `infrastructure/scripts/` не ссылается на Python-бэкенд
  (Step 10 уже перевёл их на jar), `technology.md` не упоминает `requirements*.txt`.

## Чекбокс 2: pyproject.toml → acceptance

- Change: корневой `pyproject.toml` оставлен как единственный Python-конфиг репозитория:
  `testpaths = ["acceptance"]`, `pythonpath = ["acceptance"]`, секции `[tool.coverage.*]`
  и игнор `UP042` (относились только к backend) удалены.
- Зависимости acceptance-набора объявлены в `[dependency-groups] acceptance` (PEP 735):
  `pytest`, `pytest-asyncio`, `httpx`, `tenacity` из бывшего `requirements-dev.txt` плюс
  `asyncpg` и `redis`, которые раньше приезжали транзитивно через `uwords-adapter-storage` /
  `uwords-adapter-cache`. Без этого удаление `requirements*.txt` оставило бы набор без
  объявленных зависимостей.
- Из `.venv` удалены editable-пакеты `uwords-*`, чтобы прогон не опирался на удалённый код.
- `ruff check acceptance`: All checks passed.

## Проверка

- Стек поднят по `run-infra.sh` → `migrate.sh` (12 changeset-ов) → `run-backend.sh`
  (bootJar пересобран из чистого Java-дерева, `/health` → `{"status":"UP","database":"UP"}`).
- Acceptance: 124 passed, 20 skipped in 254.90s -- идентично Step 12; тесты не редактировались.
- Gradle: `./gradlew build -x test` и `:backend:architecture:test` зелёные после удаления.
