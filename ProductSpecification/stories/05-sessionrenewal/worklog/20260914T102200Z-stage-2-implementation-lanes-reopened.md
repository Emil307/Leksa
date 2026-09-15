# 2.1 Действующая сессия получает новую пару токенов — stage-2 implementation lanes (reopened)

Started: 2026-09-14T10:22:00Z

Outcome: completed

- Область: переоткрытые полосы usecase + application (уникальный claim access-токена),
  по записи `20260914T094149Z-stage-1-acceptance-lane-reopened.md`. Полосы rest и storage
  сохраняют чекпоинты PASS (`33f51f2`/`b5479bb`/`4fa82fd`).
- Шов заморожен координатором до диспетчеризации (иначе полосы имели бы зависимость по
  сигнатуре `AccessTokenClaims`): `f7da3ba` — `AccessTokenClaims.tokenId`,
  `Session.accessTokenClaims(tokenId, now, policy)`, `RefreshSessionTokensService(…, ids, …)`,
  оба выпускающих usecase берут id из `IdGeneratorPort`; `JwtAccessTokenIssuer` не тронут.
  После шва: usecase 26, application 24, architecture 5 — все passed.
- Решение дополнено: `decisions/token-rotation-contracts-decision.md`, раздел от 2026-09-14
  (`jti` + `aud = uwords-api`, чтобы токен принимал guard Story 4).

## Чекпоинты полос

- usecase RED `5d80bc4` — ALREADY_GREEN (шов `f7da3ba` уже подаёт `ids.newId()` в refresh):
  `RefreshSessionRotatesTokensTest.shouldMintTheRefreshedAccessTokenWithAFreshTokenId`,
  Statements сравнивают полный список выпущенных `AccessTokenClaims` (login + refresh).
  Test-review: 1 находка исправлена (проекция только на tokenId → полные claims). usecase 27 passed.
- usecase coverage (report-only): строки дельты покрыты на 100 %; пробелов для 2.1 нет.
  Непокрытое вне дельты: `RefreshSessionTokensService` L61–67 (Tier 2 3.1/3.3),
  `Session.isExpiredAt` ветка «истёк» (Tier 2 3.2, вызывается только из фейка),
  `VerifyAuthChallengeService.claim` L86–87 (Story 4). JaCoCo в билде не объявлен —
  отчёт снят через init-скрипт вне репозитория.
- application RED `5350b38`: `SecurityTokenTest` +3 (`@Disabled`) — ровно пять claims,
  два tokenId → два разных токена, guard Story 4 принимает выпущенный токен.
  Предсказание = факт: `jti` null; токены байт-идентичны; `UnauthorizedException`
  в `VerifiedAccessToken.requireApiAudience`. Test-review: 2 находки исправлены
  (структурное сравнение payload, точный payload обоих токенов при `isNotEqualTo`).
- application GREEN `fe50819`: `JwtAccessTokenIssuer` подписывает `sub, sid, jti, exp, aud`;
  маркеры сняты. application 27 passed / 0 skipped, architecture 5 passed.
- refactor `f3c352e` (детекторы M/D/T → refactor-agent, 9 применено): `AccessTokenClaims.of`
  (домен владеет расчётом expiry, `Session` и `verified()` делегируют); issuer передаёт
  `Instant` в `withExpiresAt`, `numericDate` удалён; вложенные вызовы портов в обоих usecase
  вынесены в локали/методы (`mintAccessToken`, `redeem`, `issuanceRequest`); `payloadOf`
  в Statements заменён на `decoder.decode`; `CallJournal.since/payloadsOf`; `FakeClock` удалён;
  `PreparedValues.take` generic; `AccessTokenData` — inline локали/параметра.
  NO ACTION: `rotateRefreshToken` preserve-whole-object (порт + storage, вне полос),
  `AccessTokenClaims` vs `VerifiedAccessToken` (issued/verified намеренно), лестница
  `claimsOf`, квалифицированные enum (конвенция репо), A40 формулы в `AuthVerifyFixtures`.
  usecase 27, application 27, architecture 5 — passed, 0 skipped.

<!-- stage-2-plan (reopened):
usecase: unit=RefreshSessionTokensService.refresh + VerifyAuthChallengeService.verify (выпуск claims); writes=[backend/usecase/src/test/java/com/uwords/usecase/service/auth/RefreshSessionRotatesTokensTest.java: кейс — свежий tokenId на каждую ротацию, отличный от login-выпуска, backend/usecase/src/test/java/com/uwords/usecase/testing/statements/RefreshSessionStatements.java: Statements для tokenId, backend/usecase/src/test/java/com/uwords/usecase/testing/statements/RefreshSessionData.java: ожидания tokenId, backend/usecase/src/main/java/com/uwords/usecase/service/auth/RefreshSessionTokensService.java: только если RED укажет дефект]; frozen-surfaces=[AccessTokenClaims(subject, sessionId, tokenId, expiresAt), Session.accessTokenClaims, IdGeneratorPort.newId, RefreshSessionTokensService(ctor после f7da3ba)]
application: unit=JwtAccessTokenIssuer.issue; writes=[backend/application/src/main/java/com/uwords/application/security/JwtAccessTokenIssuer.java: подписывать jti и aud, backend/application/src/test/java/com/uwords/application/SecurityTokenTest.java: кейсы jti/aud и различие двух выпусков в одну секунду, backend/application/src/test/java/com/uwords/application/testing/statements/SecurityTokenStatements.java: Statements для jti/aud]; frozen-surfaces=[AccessTokenIssuerPort.issue, AccessTokenClaims, VerifiedAccessToken.API_AUDIENCE/TOKEN_ID_CLAIM, AuthTokenProperties, ALGORITHM HS256]
-->
<!-- lanes: rest={red:af4fd9b,green:33f51f2,refactor:NO_CHANGE} PASS; storage={red:0fd0150,green:b5479bb,refactor:4fa82fd} PASS; usecase={seam:f7da3ba,red:5d80bc4 ALREADY_GREEN,coverage:REPORT_ONLY,refactor:f3c352e} PASS; application={seam:f7da3ba,red:5350b38,green:fe50819,refactor:f3c352e} PASS -->
