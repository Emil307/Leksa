# Task 2: Java 21 Backend Rewrite -- Progress

Type: refactor

## Spec
- [x] spec
- [x] design
- [x] refactor (steps discovery) (plan: +39/-0/~0)

## Work

### Step 1: Gradle-скелет и модуль архитектуры
- [x] settings.gradle.kts, корневой build.gradle.kts, toolchain 21, bootJar только у :backend:application, восемь module-файлов
- [x] ArchUnit-правила в :backend:architecture: направление зависимостей, нет фреймворка в domain/usecase, usecase не зовёт usecase
- [x] проверка: ./gradlew build -x test и ./gradlew :backend:architecture:test зелёные

### Step 2: backend/domain
- [x] перенос 36 доменных типов на records/enums/интерфейсы, пакет com.uwords.domain, только Lombok, без Spring
- [x] toLowerCase(Locale.ROOT) в нормализации email, ручное редактирование секретов в toString() у 6 типов, Math.ceil на true-division в ttl_seconds
- [S] юнит-тестов домена в Python нет, переносить нечего; ./gradlew :backend:domain:build зелёный

### Step 3: backend/usecase
- [x] перенос 14 портов и 6 сервисов, только @Service; @Transactional нет нигде -- в Python транзакции демаркирует storage, не usecase
- [x] перенос юнит-тестов usecase вместе с Fakes и Statements, проверка ./gradlew :backend:usecase:test

### Step 4: Liquibase changelog
- [x] changelog воссоздаёт схемы auth и notifications с нуля, spring.liquibase.enabled=false, миграции только из migrate.sh
- [x] построчная сверка с пятью Alembic-ревизиями: функциональный уникальный индекс на lower(btrim(email)), enum auth.user_gender, NOT NULL expires_at, JSONB data
- [x] проверка: SQL из clear-acceptance-data.sh проходит против воссозданной схемы

### Step 5: backend/adapters/storage
- [x] перенос 4 моделей, 4 мапперов, 6 репозиториев, unit_of_work, outbox_queue, engine, health; Instant, entityManager.persist(), без JPA-ассоциаций, ddl-auto=validate
- [x] created_at/updated_at остаются на часах БД: только @DynamicInsert; insertable=false отвергнут -- SessionIssuanceMapper пишет created_at явно
- [x] gender как String с ручным конвертером, чтобы сохранить UnavailableException и 503 вместо 500 от Hibernate
- [x] явный statement_timeout и размер пула Hikari заданы в StorageDataSourceConfiguration из DbProperties, без adapter-level application.yml
- [x] перенос юнит-тестов storage на Testcontainers, проверка ./gradlew :backend:adapters:storage:test

### Step 6: backend/adapters/cache
- [x] четыре Lua-скрипта переносятся дословно в src/main/resources/redis, подстановка плейсхолдеров через String.replace, не String.format
- [x] сериализация Redis-записи даёт createdAt в формате +00:00, а не Z, иначе лексическое сравнение в swap-challenge инвертируется
- [x] ключи и TTL те же, StringRedisTemplate, без @EnableRedisRepositories, явные socket- и command-таймауты; пула нет -- Lettuce мультиплексирует одно соединение
- [x] перенос юнит-тестов cache с фейковым RedisTemplate, ассертящим текст скрипта и порядок KEYS/ARGV

### Step 7: backend/adapters/email
- [x] JavaMailSender и MimeMessageHelper(msg, false, "UTF-8"), явный таймаут отправки
- [x] перенос юнит-тестов email на GreenMail, проверка ./gradlew :backend:adapters:email:test

### Step 8: backend/adapters/rest
- [x] перенос 5 контроллеров и DTO; поля challengeId и code типа Object/JsonNode, @JsonIgnoreProperties(ignoreUnknown), без Bean Validation
- [x] GlobalExceptionHandler покрывает BaseDomainException, UnauthorizedException с payload null, Jackson- и media-type-отказы и Exception; whitelabel и problemdetails выключены
- [x] AccessTokenInterceptor и HandlerMethodArgumentResolver вместо Spring Security, addPathPatterns только на /api/v1/profile
- [x] health-контроллер на /health с плоским телом status/database, не actuator
- [x] перенос юнит-тестов rest на MockMvc, проверка ./gradlew :backend:adapters:rest:test

### Step 9: backend/application
- [x] UwordsApplication, конфигурации wiring, @ConfigurationProperties с @Validated на JWT_SECRET и обоим TTL, application.yml с теми же именами переменных
- [x] JwtAccessTokenIssuer и JwtAccessTokenDecoder: подпись проверяется, exp и aud библиотекой не проверяются, истечение остаётся за доменом
- [x] ConfigurationProbe: отдельный main-класс, биндит properties без web/DB/Redis, выход ≠0 с именем переменной в stderr
- [x] spring.threads.virtual.enabled, max-http-request-header-size 16KB, encoding UTF-8 force, write-dates-as-timestamps false, сессии сервлета выключены
- [x] optionalLayer в LayerDependencyRulesTest возвращён в layer: все четыре слоя заполнены
- [x] перенос юнит-тестов application с Clock.fixed, проверка ./gradlew :backend:application:test

### Step 10: infrastructure и technology.md
- [x] _env.sh получает app_jar и java_bin, run-backend.sh запускает jar, migrate.sh вызывает liquibase-задачу, stop-backend.sh не меняется
- [x] окна ожидания health в test-acceptance.sh и таймауты boot-проб подняты под холодный старт JVM
- [x] MAIL_TIMEOUT_MILLIS добавлен в infrastructure/.env: новая переменная из Step 7, дефолт 60000 держит паритет с aiosmtplib
- [x] technology.md переписан на java-spring, включая переопределение health на /health вместо /actuator/health

### Step 11: boot-пробы acceptance-набора
- [x] configuration_startup_statements.py и signing_secret_boot_statements.py переключены на JVM-пробник; сами тесты не трогаются

### Step 12: приёмка
- [x] весь Python acceptance-набор зелёный против Java-бэкенда без правок самих тестов: 124 passed, 20 skipped

### Step 13: удаление Python-бэкенда
- [x] одним коммитом удалить backend/**/src и backend/**/tests на Python, .importlinter, requirements*.txt, backend-секции pyproject.toml
- [x] testpaths в pyproject.toml переведён на acceptance, проверка: acceptance-набор остаётся зелёным
