# 2.1 Действующая сессия получает новую пару токенов — approve stage-1 contracts

Started: 2026-09-03T00:00:00Z

Outcome: completed

- Decision: пользователь утвердил контракты Stage 1 без изменений, в постреструктурном виде.
- Reviewed: приёмочная цель `TestTokenRefreshAcceptance` (1 кейс `test_should_rotate_both_tokens_and_keep_the_session_identifier`, 4 Then-клаузы: 200, неизменный `id`, оба токена новые, поля ровно `session{id,refreshToken,accessToken}`), RED — ни `POST /api/v1/auth/challenge/start`, ни `POST /api/v1/auth/token/refresh` ещё не смонтированы.
- Frozen (domain): `RefreshToken.of/matches` + `MAX_TOKEN_BYTES=512` + редактированный repr, `SessionPolicy.of/access_expiry_at/refresh_expiry_at/truncate`, `Session.is_expired_at/rotate/access_token_claims`, `AccessTokenClaims{subject,session_id,expires_at}.numeric_date`.
- Frozen (usecase): `SessionRepositoryPort.find_active_by_refresh_token/rotate_refresh_token`, `RefreshTokenGeneratorPort.generate`, `AccessTokenIssuerPort.issue`, `ClockPort.now`, `RefreshSessionRequest`, `RotatedSessionTokens`, `RefreshSessionTokensService.__init__`.
- Frozen (adapters/application): `SessionEntity` (`auth.t_sessions`, `ix_t_sessions_user_id`, `uq_t_sessions_refresh_token`), ревизия `0001_auth_sessions`; `TOKEN_PREFIX`, `POST /refresh`, `SessionRefreshRequest.refreshToken`, `RotatedSessionSchema`, `SessionRefreshResponse.session`; `ALGORITHM="HS256"`, `TOKEN_BYTES=32`, `AuthTokenSettings`, `create_auth_token_router`.
- Ordering contracts: пара минтится и подписывается до любой записи; авторитет успеха — rowcount одного условного UPDATE с предикатом по токену и `expires_at`.
- Path note: контракты пережили рефакторинг доменных пакетов (`domain/auth/session/`) и группировку портов (`usecase/ports/auth/session/`, `ports/system/clock.py`); символьные поверхности не изменились.
- Decision record: `decisions/token-rotation-contracts-decision.md`.
- Lane plan: четыре непересекающиеся линии — usecase, adapter-storage, adapter-rest, application; манифест сохранён на чекбоксе `stage-2 implementation lanes`.
- Stage-1 commits: acceptance `688d65d`, `9d8ab7e`; design `44ad11f`.

<!-- stage-1-approval: granted; stage-2 advanced -->
