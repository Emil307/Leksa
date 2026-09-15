# Stage 2 — implementation lanes (сценарий 4.1)

Outcome: сценарий 4.1 «Существующий пользователь получает сессию по верному коду» реализован пятью
параллельными полосами; координатор опубликовал три коммита — RED (`be90ddf`), GREEN (`d83a500`) и
отдельный рефакторинг (`e1593b3`). Приёмочный тест остаётся отключённым до stage 3.

## Нормализация утверждённого плана

План полос взят из записи stage 1 без изменений. Владение путями осталось непересекающимся, ни одна
полоса не ставила и не коммитила ничего сама — публикацию целиком вёл координатор.

## Контрольные точки полос

| полоса | RED | GREEN | пути (кратко) |
|---|---|---|---|
| usecase | пройдена | пройдена | `usecase/services/auth/verify_challenge.py`, порты `auth/challenge`, `auth/session`, `usecase/tests/**` |
| adapter-cache | пройдена | пройдена | `adapter_cache/verification_store.py`, `keys.py`, `cache/tests/**` |
| adapter-storage | пройдена | пройдена | `adapter_storage/{mappers,repositories}/session_issuance.py`, миграция `0004_auth_accounts`, `storage/tests/**` |
| adapter-rest | пройдена | пройдена | `adapter_rest/routers/auth_verify.py`, схемы, `rest/tests/**` |
| application | пройдена | пройдена | `application/{wiring,main,settings}.py`, `security/*`, `application/tests/**` |

Коммит A (`be90ddf`, 26 файлов) — только деревья тестов, каждый целевой класс со своим skip-маркером:
36 passed, 23 skipped. Коммит B (`d83a500`, 26 файлов) — весь продакшен плюс дельта «снять маркер»:
59 passed. Рефакторинг опубликован отдельно (`e1593b3`) после совместной проверки.

Совместная проверка на HEAD: `59 passed`, `ruff check backend acceptance` — All checks passed,
`lint-imports` — 1 kept / 0 broken, ни одного файла свыше 200 строк.

## Отклонения от утверждённых манифестов

- Полоса usecase намеренно не реализовала ветки отказа (неизвестный challenge, исчерпанные попытки,
  проигранная гонка redeem): они принадлежат сценариям 4.2, 5.1 и 6.1.
- Сервис бросает `UnauthorizedException` напрямую: у `AuthFailureReason` нет значения для challenge,
  а `reason.py` не входил в манифест полосы.
- Миграция `0004_auth_accounts` добавлена полосой storage сверх манифеста — без неё таблица `t_auth`
  не существует и GREEN недостижим.

## Дефект шва, закрытый координатором

`assert_redeemed_challenge_is_remembered_for_replay` утверждал, что в хранилище повторов ровно одна
запись, тогда как Given сам выполняет полный успешный verify и записей законно две. Ассерт переписан
на обе записи (`...0001` из Given и `...0004` из проверенного challenge) плюс TTL=60 согласно
`remember_verification`. Продакшен не менялся.

## Сбой подчинённого шага

Серийный `refactor-agent` прервался на ошибке аутентификации API (403, `authentication_failed`)
примерно на 17-м из 23 пунктов утверждённого списка. Оставленное им дерево было зелёным; координатор
доделал оставшиеся пункты вручную и опубликовал результат как `e1593b3`.

## Находки, вынесенные за пределы stage 2 (здесь не исправлены)

- `JWT_SECRET=local-development-only-secret` — 29 байт против рекомендованных 32 для HS256; PyJWT
  печатает `InsecureKeyLengthWarning`. Правка лежит в `infrastructure/.env`, `.env.example` и
  `setup-ports.sh` — вне манифеста полос.
- Неизвестный или истёкший `challengeId` сейчас даёт 500 вместо 401 — до сценариев 4.2/5.1/5.4/6.1.
- `SessionPolicy.of()` со своей проверкой положительного TTL обходится напрямую в `settings.py`.
- `mappers/session_issuance.py` порождает идентификатор строки `t_auth` через `uuid4()` внутри
  адаптера, что противоречит правилу ADR «идентификаторы порождаются в usecase».
- Схема JSON-записи Redis продублирована в четырёх местах.
- Отклонены при разборе как изменения контракта, а не рефакторинг: конвертация dict-маппера в
  сущность, удаление `challengeId` из JSON повтора, общая `SessionTokensSchema` со заглушкой
  story 5, `StoredChallenge.of/with_attempts`.
