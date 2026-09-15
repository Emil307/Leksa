# Step 10: infrastructure и technology.md

## Что сделано

- `infrastructure/scripts/_env.sh`: добавлены `java_bin()` (уважает `JAVA_HOME`, иначе `java` из PATH) и
  `app_jar()` (ищет `backend/application/build/libs/*.jar`, отбрасывает `-plain.jar`, при отсутствии
  печатает подсказку про `:backend:application:bootJar` и возвращает 1).
- `infrastructure/scripts/run-backend.sh`: вместо uvicorn собирает `:backend:application:bootJar`
  и делает `exec "$(java_bin)" -jar "$jar" "$@"`. Порт и хост по-прежнему приходят из `infrastructure/.env`.
- `infrastructure/scripts/migrate.sh`: вместо `alembic upgrade head` экспортирует `LIQUIBASE_URL`,
  `LIQUIBASE_USERNAME`, `LIQUIBASE_PASSWORD` из `.env` и вызывает
  `:backend:adapters:storage:liquibaseUpdate`.
- `infrastructure/scripts/stop-backend.sh` не менялся: он останавливает по PID/порту, а не по имени процесса.
- `infrastructure/scripts/test-acceptance.sh`: окно ожидания health поднято с `seq 1 30` до `seq 1 90`
  под холодный старт JVM.
- `acceptance/statements/configuration_startup_statements.py`: `STARTUP_TIMEOUT_SECONDS` 25 -> 60
  (в `signing_secret_boot_statements.py` уже было 60). Сами тесты не тронуты.
- `MAIL_TIMEOUT_MILLIS=60000` добавлен в `infrastructure/.env`, `.env.example` и `setup-ports.sh`
  сразу после `MAIL_SENDER`.
- `ProductSpecification/technology.md` переписан на профиль `java-spring`: таблицы Backend и Testing,
  строка `Application server | embedded Tomcat`, Module Layout на Gradle-проекты и пакеты `com.uwords.*`,
  Testing Layers на `src/test/java/`, Conventions (`@Disabled("RED: ...")`, `UnsupportedOperationException`,
  `./gradlew :backend:{module}:test`, путь JaCoCo, health на `/health`, `migrate.sh` -> `liquibaseUpdate`,
  строка про `ConfigurationProbe`, строка про ArchUnit, `${VAR:fallback}` против `${VAR:-fallback}`,
  запрет `./gradlew --stop`).

## Проверки

- `./gradlew :backend:application:bootJar` -> `application-0.1.0.jar` + `application-0.1.0-plain.jar`.
- Локальная инфраструктура поднята (postgres 5433, redis 6380, mailhog 8026, проект `uwords-1`).
- `migrate.sh` против пустой базы `uwords_migrate_check`: 12 changeset'ов, `Update has been successful`.

## Открытый вопрос: схема общей dev-базы

`migrate.sh` против штатной базы `uwords` падает на
`0003-auth-sessions.xml::0003-02-index-ix-t-sessions-user-id` -- `relation "ix_t_sessions_user_id"
already exists`. Причина не в скрипте: база несёт схему, созданную Alembic, а по решению задачи
Liquibase-changelog накатывается с нуля и baseline не предусмотрен. Wiring скрипта подтверждён на
отдельной пустой базе; общую базу перед Step 12 надо пересоздать (drop schema auth, notifications,
public.alembic_version -- либо пересоздать том). Сброс схемы заблокирован классификатором и требует
решения пользователя. Разрушать существующую базу самостоятельно не стал.
