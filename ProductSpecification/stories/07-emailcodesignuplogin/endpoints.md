# EmailCodeSignupLogin — эндпоинты API

Новых эндпоинтов история не вводит: фронт — потребитель контрактов истории 01.
Схемы не меняются, YAML переиспользуются как есть.

| Метод | Путь | Описание | Спецификация |
|--------|------|-------------|---|
| POST | /api/v1/auth/challenge/start | Экран почты и «Отправить новый код»: `{email, challengeType: "EMAIL_CODE"}` → `{challengeId, challengeType, expiresAt}` | `ProductSpecification/api-specs/auth_challenge_start.yaml` |
| POST | /api/v1/auth/challenge/verify | Экран кода: `{challengeId, code}` → `{user{id}, session{id, accessToken, refreshToken}}` | `ProductSpecification/api-specs/auth_challenge_verify.yaml` |

## Как фронт читает ответы

| Ответ | Экран | Реакция |
|---|---|---|
| `start` 200 | почта → код | запомнить `challengeId` и `expiresAt`, показать адрес и отсчёт до `expiresAt`; на экране кода — сбросить введённый код и заменить `challengeId`/`expiresAt` |
| `start` 400 `VALIDATION_FAILED` | почта | «Проверьте адрес», остаёмся на экране почты |
| `start` 409 `CONFLICT` | почта / код | кнопка закрывается на `payload.retryAfterSeconds` с обратным отсчётом; на экране кода поле кода остаётся открытым |
| `start` 503 `UNAVAILABLE` | почта / код | «Сервис временно недоступен», кнопка снова доступна |
| `verify` 200 | код → внутри | сессия в памяти; ни `session.id`, ни токены на экран не выводятся |
| `verify` 401 `UNAUTHORIZED` (любое `message`) | код | одно сообщение, поле открыто |
| `verify` 400 `VALIDATION_FAILED` | код | как 401 — при шести цифрах и UUID из `start` недостижимо |
| `verify` 503 `UNAVAILABLE` | код | «Сервис временно недоступен», введённый код сохраняется |

## Заметки

- **Поля `message` и `challengeType` в ответах фронт не использует.** Тексты — свои, по `code`
  и HTTP-статусу; `challengeType` всегда `EMAIL_CODE`.
- **Длительность кулдауна в ответе `start` не приходит** — только в `409`. Поэтому кнопка
  повтора открыта до первого `409`; бэкенд не меняем (см. Notes истории).
- **Текущее состояние по acceptance-сьюту** (`acceptance/tests/backend/auth/`): включены
  `start` (200/400/409 с отсчётом), `verify` (200, регистрация, ведущий ноль, неверный код
  401, второй вход). Ещё RED и на фронт не влияют по контракту, но влияют на E2E-стаб:
  `test_challenge_resend_acceptance.py` (после повторного `start` старый код даёт 500 вместо
  401), `test_expired_and_unknown_challenge_acceptance.py`, `test_terminal_challenge_acceptance.py`.
  Стаб для E2E моделирует **целевое** поведение — 401.
- Идемпотентность `verify` в окне повтора (тот же `session.id`) для фронта не важна: второй
  запрос он не отправляет — кнопка блокируется на время ожидания.
