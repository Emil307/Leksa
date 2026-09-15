# Step 1: Gradle-скелет и модуль архитектуры

Started: 2026-09-10T00:05:00Z

Outcome: completed

- Change: в репозитории не было ни Gradle, ни wrapper'а. Дистрибутив 8.10.2 скачан
  в скретчпад сессии, `gradle wrapper` запущен один раз из него; в репозиторий лёг
  обычный коммитимый wrapper (`gradlew`, `gradlew.bat`, `gradle/wrapper/`).
  В `.gitignore` добавлен `.gradle/`; `build/` там уже был.
- Change: `settings.gradle.kts` включает восемь модулей. Промежуточные проекты
  `:backend` и `:backend:adapters` собственных build-файлов не имеют — они пустые
  контейнеры пути.
- Change: корневой `build.gradle.kts` держит toolchain 21, Spring Boot BOM 3.3.4
  через `io.spring.dependency-management`, Lombok/JUnit 5/AssertJ во всех
  подпроектах и `useJUnitPlatform()`. Плагин Boot применён `apply false` и включён
  только в `:backend:application`, где `bootJar` и живёт.
- Change: `:backend:application` объявляет `mainClass` явно
  (`com.uwords.application.UwordsApplication`). Без этого `bootJar` падает на
  сканировании main-класса, которого до Step 9 не существует; явное имя переводит
  резолвинг в запись манифеста. Плоский jar включён обратно с классификатором
  `plain`, иначе `:backend:architecture` не видит классы application.
- Change: `:backend:architecture` — тестовый модуль, ArchUnit 1.3.0. Правила:
  направление зависимостей (layeredArchitecture), отсутствие Spring/Jakarta/Jackson/
  Hibernate в domain, в usecase только `stereotype` и `transaction`, usecase не
  зависит от usecase, контроллер не зависит от контроллера.
- Tests: `./gradlew build -x test` — BUILD SUCCESSFUL, 13 задач.
  `./gradlew :backend:architecture:test` — 5 тестов, 5 прошли, 0 упали.
  `./gradlew :backend:application:bootJar` — jar 62 МБ собирается.

## Отклонение: слои объявлены optionalLayer

Первый прогон `dependenciesFlowInward` упал четырьмя нарушениями «Layer is empty» —
production-классов ещё нет ни в одном модуле. `archRule.failOnEmptyShould=false` в
`archunit.properties` на проверку пустых слоёв в `layeredArchitecture` не влияет.

Слои временно объявлены `optionalLayer`. Это ослабление: опечатка в имени пакета
сделает слой пустым, и правило пройдёт молча. Компенсация — отдельный чекбокс в
Step 9, где заполняется последний модуль: вернуть `layer` вместо `optionalLayer` и
убедиться, что тест по-прежнему зелёный. До Step 9 правило проверяет направление
зависимостей между теми слоями, которые уже непусты, — то есть ровно то, ради чего
оно стоит первым в плане.

## Что осталось за скобками

- `archunit.properties` с `archRule.failOnEmptyShould=false` оставлен: правила
  `noClasses().should()` иначе падают на пустом импорте по той же причине. Их
  предметность возвращается сама, как только появляются классы.
- Версии `com.auth0:java-jwt`, `com.icegreen:greenmail-junit5`,
  `com.tngtech.archunit:archunit-junit5` закреплены явно — их нет в Boot BOM.
