# Step 9: backend/application

Type: refactor work step (Task 2)

## Что перенесено

- `UwordsApplication` (`scanBasePackages = "com.uwords"`), `SystemClock`, `UuidGenerator`,
  `SecureNumericCodeGenerator`, `SecureRandomRefreshTokenGenerator`, `JwtAccessTokenIssuer`,
  `JwtAccessTokenDecoder`, `DomainPolicyConfiguration`, три `@ConfigurationProperties`-записи и
  `ConfigurationProbe`.
- `application.yml`: имена переменных окружения совпадают с Python (`JWT_SECRET`,
  `ACCESS_TOKEN_TTL_SECONDS`, `AUTH_CHALLENGE_*`, `MAIL_*`, `DB_*`, `REDIS_*`).
- Юнит-тесты: 24 Java-теста против 24 Python-тестов (`.venv/bin/pytest backend/application/tests -q`
  из корня репозитория -- 24 passed).

## Проверки

- `./gradlew :backend:application:test :backend:architecture:test` -- BUILD SUCCESSFUL,
  application 24 passed, architecture 5 passed.
- `LayerDependencyRulesTest`: `optionalLayer` возвращён в `layer` для всех четырёх слоёв.

## Расхождения с Python-оригиналом

1. Маршруты проверяются через `RequestMappingHandlerMapping`, а не через OpenAPI-документ:
   springdoc намеренно не на classpath, `app.openapi()["paths"]` эквивалента не имеет.
2. Схема ответа профиля проверяется типом возврата обработчика
   (`ResponseEntity<UserProfileResponseDto>` через `ResolvableType`), а не `$ref` на схему.
3. Охраняемость профиля проверяется наличием `AccessTokenInterceptor` в цепочке обработчика --
   в Python guard был зависимостью маршрута и в OpenAPI не виден вовсе.
4. `test_should_refuse_to_boot_without_a_signing_secret` перенесён на `ApplicationContextRunner`
   (`SigningSecretBootTest`) -- отдельный контекст без контейнера; проверяется, что корневая
   причина называет `auth.token` и `jwtSecret`.
5. `test_should_answer_a_timezone_aware_utc_instant` заменён на проверку, что `Instant`
   не зависит от зоны часов (`Clock.fixed` с +03:00 даёт тот же инстант): в Java `Instant`
   по определению не носит зону, а Python возвращал `datetime` с tzinfo.
6. `monkeypatch` на `secrets.randbelow` заменён на `ScriptedDigits implements RandomGenerator`,
   переданный в конструктор генератора.
7. Полный boot-тест поднимает Testcontainers postgres (`postgres:17-alpine`); Redis и SMTP
   подключаются лениво и стабов не требуют.
8. `AuthTokenProperties` требует положительных TTL, поэтому boot-тест задаёт их через
   `@DynamicPropertySource` -- в `application.yml` дефолт `0`, чтобы `@Positive` называл переменную.

## Заметки

- У `SystemClock`, `SecureNumericCodeGenerator` и `JwtAccessTokenDecoder` по два конструктора
  только у первых двух; Spring в этом случае берёт конструктор без аргументов. У обоих JWT-классов
  конструктор ровно один (`AuthTokenProperties`), чтобы не зависеть от этого правила.
