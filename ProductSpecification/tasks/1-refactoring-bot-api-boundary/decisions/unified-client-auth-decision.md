# Decision: Единая JWT-аутентификация клиентов

**Date**: 2026-08-14 **Task**: 1

API должен одинаково авторизовывать frontend и Telegram-бот через общий challenge
lifecycle, сохраняя провайдера только стратегией проверки личности, а не частью
продуктовых контрактов. Базовая модель challenge впервые зафиксирована в
[Story 1 — EmailCodeLogin](../../../stories/01-emailcodelogin/interview.md).

| Rejected | Why |
|----------|-----|
| Service credential и `telegram_id` в каждом продуктовом запросе | Telegram-провайдер проникает во все endpoints и создаёт отдельный режим авторизации для бота. |
| Отдельный `POST /api/v1/auth/telegram/exchange` | Провайдер получает собственный login lifecycle вместо общей пары challenge endpoints. |
| Отдельные типы пользовательских токенов для frontend и бота | Клиенты получают разные контракты сессии и разные middleware авторизации. |
| Плавный переход со старой базой бота | Прода и сохраняемых production-данных ещё нет, поэтому временная совместимость только усложняет систему. |

**Chosen**: все способы входа используют `POST /api/v1/auth/challenge/start` и
`POST /api/v1/auth/challenge/verify`; конкретный провайдер выбирается по
`challengeType`. `EMAIL_CODE`, `TG` и будущий `OAUTH` являются стратегиями одного
lifecycle, а не отдельными login endpoints. Успешный `verify` выдаёт всем клиентам
одинаковую пару `access JWT` и `refresh JWT`. После этого продуктовые endpoints
получают только access token и не знают ни о провайдере, ни о типе клиента. Переход
выполняется прямым переключением без параллельной работы старой и новой продуктовых
моделей.

## Model

- `ExternalIdentity`: `provider`, строковый `subject`, `user_id`; пара
  `(provider, subject)` уникальна.
- `ClientApplication`: канал и audience пользовательской сессии. Bot является
  confidential client с ротируемым service credential; frontend является public
  client и не хранит общий секрет.
- `UserSession`: внутренняя пользовательская сессия, не привязанная к провайдеру
  входа.
- `ChallengeStrategy`: по `challengeType` определяет provider-specific входные
  данные, ключ уникальности и способ проверки доказательства; общий lifecycle и
  выдача сессии от стратегии не зависят.
- Access JWT содержит внутренний user/session identity, audience, expiry и `jti`,
  но не `telegram_id`; он короткоживущий и используется на всех продуктовых
  endpoints.
- Refresh JWT относится к той же `UserSession`, ротируется при использовании, а
  повтор уже использованного refresh token отзывает его session family.
- Telegram-стратегия работает только через общие challenge endpoints; отдельного
  `/api/v1/auth/telegram/exchange` нет.
- Bot client подтверждает себя на границе Telegram challenge, а стратегия проверяет
  Telegram evidence до создания или поиска `User` и `ExternalIdentity`.
- `POST /api/v1/auth/refresh` не зависит от способа входа и одинаков для frontend и
  бота.
- Claims, rotation и revocation одинаковы для клиентов; способ доставки и хранения
  токенов определяется безопасностью внешнего client boundary.
- Бот хранит пару токенов только в Redis с TTL не дольше их expiry; потеря Redis
  приводит к новому Telegram challenge, а не к чтению продуктовой базы.

## Edge Cases

| Case | Behavior |
|------|----------|
| Telegram challenge без корректной аутентификации bot client | Отклоняется до обработки Telegram evidence. |
| Поддельный `telegram_id` отправлен прямо в продуктовый endpoint | Игнорируется как неизвестное поле либо отклоняется; пользователь определяется только по access JWT. |
| Два Telegram challenge одновременно подтверждают одну identity | Уникальность `(provider, subject)` оставляет одного пользователя и одну привязку без orphan-записей. |
| Access JWT истёк | Клиент использует provider-neutral refresh endpoint. |
| Refresh JWT повторно использован после ротации | Вся session family отзывается, повтор не выдаёт новую пару токенов. |
| Redis бота потерян или очищен | Бот начинает новый Telegram challenge и продолжает без локальной продуктовой базы. |
| Переключение на новый API | Старые PostgreSQL repositories бота не используются; переходного dual-write или чтения старой базы нет. |
