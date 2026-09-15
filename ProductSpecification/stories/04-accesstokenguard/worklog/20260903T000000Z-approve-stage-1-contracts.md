# 1.1 Пользователь с действующей сессией получает всю свою запись — approve stage-1 contracts

Started: 2026-09-03T00:00:00Z

Outcome: completed

- Decision: пользователь утвердил контракты Stage 1 без изменений.
- Reviewed: приёмочная цель `TestProfileReadAcceptance` (1 кейс, 5 Then-клауз, RED по отсутствию `auth.t_users` и маршрута `GET /api/v1/profile`).
- Frozen: домен (`BearerCredential.of`, `VerifiedAccessToken`, `ActiveSession.authorizes`, `User`, `Gender.parse`), порты (`AccessTokenDecoderPort.decode`, `ActiveSessionRepositoryPort.find_by_id`, `UserRepositoryPort.find_by_id`, `ClockPort.now`), rest (`UserProfileResponse`, `UNAUTHORIZED_BODY`, `PROFILE_PATH`), storage (`UserEntity`, ревизия `0002_auth_users`), application (`ACCEPTED_ALGORITHMS`, `AccessTokenVerificationSettings.jwt_secret`).
- Decision records: `decisions/access-token-claims-contract-decision.md`, `decisions/auth-schema-ownership-decision.md`.
- Lane plan: четыре непересекающиеся линии — usecase, adapter-storage, adapter-rest, adapter-application-security; манифест сохранён на чекбоксе `stage-2 implementation lanes`.
- Stage-1 commits: acceptance `e849029`, `db8cfa0`; design `8f12f0a`.

<!-- stage-1-approval: granted; stage-2 advanced -->
