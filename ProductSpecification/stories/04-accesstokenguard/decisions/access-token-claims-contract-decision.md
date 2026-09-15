# Decision: Контракт проверки access-токена отделён от контракта выпуска

**Date**: 2026-08-16 **Scenarios**: 1.1, 2.1, 3.1 (01_API), 2.1–2.4, 4.1–4.3 (05_Security)

История 4 требует обязательные claims `aud = "uwords-api"` и `jti` (UUID), а
параллельно идущая история 5 (SessionRenewal) уже зафиксировала `AccessTokenClaims`
ровно с `sub`, `sid`, `exp` и docstring «no other claim is added» — токены, выпущенные
сегодняшним issuer, guard отклонил бы.

| Rejected | Why |
|----------|-----|
| Расширить `AccessTokenClaims` (`domain/auth/session/access_token_claims.py`) полем `token_id` и константой `aud` | Файл принадлежит истории 5, которая идёт в этом же worktree прямо сейчас; правка её контракта из соседней истории — гарантированный конфликт и молчаливое переопределение чужого решения |
| Ослабить guard: сделать `aud` и `jti` необязательными | Прямо противоречит `04_AccessTokenGuard.md` (Validation Rules) и `interview.md` (Token/Auth Requirements); ослабление проверки ради совместимости с ещё не выпущенным issuer — это fail-open |
| Переходный период: guard принимает токены и без `aud`/`jti` | Ни один токен ещё не выпущен в продакшене (обе истории не задеплоены), поэтому grace-путь защищал бы несуществующий трафик и остался бы навсегда |

**Chosen**: сторона проверки описана самостоятельным доменным типом
`VerifiedAccessToken`, независимым от `AccessTokenClaims`. История 4 не трогает issuer.

**Требование к истории 5, без которого стороны не сойдутся**: `AccessTokenClaims`
должен получить `token_id: UUID`, а `JwtAccessTokenIssuer.issue` — ставить `aud` равным
`domain.auth.session.verified_access_token.API_AUDIENCE` и `jti` равным `token_id`. До этого
изменения токен, выпущенный `/api/v1/auth/token/refresh`, получит от guard единый `401`.
Порядок выката: issuer с `aud`/`jti` уходит в релиз не позже guard.

## Model

- `domain/auth/session/verified_access_token.py` — `VerifiedAccessToken(subject, session_id, token_id, expires_at)`,
  `of(claims: Mapping[str, object])`, `is_expired_at(now)`; `API_AUDIENCE = "uwords-api"`,
  `MIN_EXPIRY_SECONDS = 1`, `MAX_EXPIRY_SECONDS = 253402300799` — все в Unix-секундах.
- `domain/auth/session/bearer_credential.py` — `BearerCredential.of(header_value)`,
  `MAX_AUTHORIZATION_HEADER_OCTETS = 4096`, redacting `__repr__`.
- `domain/auth/session/active_session.py` — `ActiveSession.authorizes(token, now)`.
- `domain/auth/failure/` — `reason.py` — `AuthFailureReason`, `unauthorized.py` — `unauthorized(reason)`.
- `usecase/ports/auth/session/access_token_decoder.py` — подпись проверяет только allow-list `["HS256"]`;
  `exp` и `aud` библиотекой **не** проверяются, обе границы решает домен по одним часам.
- `usecase/services/auth/authenticate_request.py` — `AuthenticateRequestService.authenticate(header)`
  → `AuthenticatedCaller(user_id, session_id)`.
- `usecase/services/profile/read_user_profile.py` — `ReadUserProfileService.read(caller)`.

## Edge Cases

| Case | Behavior |
|------|----------|
| Токен без `aud` или `jti` (текущий формат истории 5) | Единый `401`, reason `claims` |
| Неизвестный лишний claim в токене | Игнорируется — не повод для отказа |
| `exp` — строка, `bool` или число вне `1..253402300799` | Единый `401`, без приведения типа |
| `aud` отличается регистром | Единый `401` — сравнение побайтное |
| Недоступность или таймаут PostgreSQL при чтении сессии/учётной записи | Единый `401`, reason `storage` — никогда не `503` и не доступ |
| Сессия есть, а строки пользователя нет | Единый `401`, reason `account` — не `404` |
| `gender` в БД содержит значение вне домена | `UnavailableException` из mapper → единый `401`, а не `500` |
