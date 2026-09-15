package com.uwords.usecase.testing.statements;

import com.uwords.domain.auth.session.AccessTokenClaims;
import com.uwords.domain.auth.session.RefreshToken;
import com.uwords.domain.auth.session.Session;
import com.uwords.domain.auth.user.ProviderAccount;
import com.uwords.usecase.service.auth.RotatedSessionTokens;
import com.uwords.usecase.testing.AuthVerifyFixtures;
import com.uwords.usecase.testing.fakes.FakeSessionRepository;
import com.uwords.usecase.testing.fakes.StubAccessTokenIssuer;
import java.time.Instant;
import java.util.List;
import java.util.Map;
import java.util.UUID;

public final class RefreshSessionData {

    public static final Instant LOGIN_AT = Instant.parse("2026-08-16T12:00:00Z");
    public static final Instant ROTATION_AT = Instant.parse("2026-08-17T09:30:00Z");
    public static final Instant LOGIN_ACCESS_EXPIRES_AT = Instant.parse("2026-08-16T12:15:00Z");
    public static final Instant ROTATED_ACCESS_EXPIRES_AT = Instant.parse("2026-08-17T09:45:00Z");
    public static final Instant ROTATED_SESSION_EXPIRES_AT = Instant.parse("2026-09-16T09:30:00Z");

    public static final UUID CHALLENGE_ID = UUID.fromString("aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa");
    public static final UUID USER_ID = UUID.fromString("bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb");
    public static final UUID SESSION_ID = UUID.fromString("cccccccc-cccc-4ccc-8ccc-cccccccccccc");
    public static final UUID LOGIN_TOKEN_ID = UUID.fromString("dddddddd-dddd-4ddd-8ddd-dddddddddddd");
    public static final UUID ROTATED_TOKEN_ID = UUID.fromString("eeeeeeee-eeee-4eee-8eee-eeeeeeeeeeee");
    public static final List<UUID> IDS = List.of(CHALLENGE_ID, USER_ID, SESSION_ID, LOGIN_TOKEN_ID);
    public static final List<UUID> ROTATION_IDS = List.of(ROTATED_TOKEN_ID);

    public static final String LOGIN_REFRESH_TOKEN = "refresh-token-issued-at-login";
    public static final String ROTATED_REFRESH_TOKEN = "refresh-token-issued-at-rotation";
    public static final String LOGIN_ACCESS_TOKEN = "access-token-issued-at-login";
    public static final String ROTATED_ACCESS_TOKEN = "access-token-issued-at-rotation";
    public static final List<String> REFRESH_TOKENS = List.of(LOGIN_REFRESH_TOKEN, ROTATED_REFRESH_TOKEN);
    public static final List<String> ACCESS_TOKENS = List.of(LOGIN_ACCESS_TOKEN, ROTATED_ACCESS_TOKEN);

    public static final RotatedSessionTokens EXPECTED_ROTATED_TOKENS =
            new RotatedSessionTokens(SESSION_ID, ROTATED_REFRESH_TOKEN, ROTATED_ACCESS_TOKEN);
    public static final AccessTokenClaims EXPECTED_LOGIN_CLAIMS =
            new AccessTokenClaims(USER_ID, SESSION_ID, LOGIN_TOKEN_ID, LOGIN_ACCESS_EXPIRES_AT);
    public static final AccessTokenClaims EXPECTED_ROTATED_CLAIMS =
            new AccessTokenClaims(USER_ID, SESSION_ID, ROTATED_TOKEN_ID, ROTATED_ACCESS_EXPIRES_AT);
    public static final List<AccessTokenClaims> EXPECTED_ISSUED_CLAIMS =
            List.of(EXPECTED_LOGIN_CLAIMS, EXPECTED_ROTATED_CLAIMS);
    public static final FakeSessionRepository.Rotation EXPECTED_ROTATION = new FakeSessionRepository.Rotation(
            SESSION_ID,
            new RefreshToken(LOGIN_REFRESH_TOKEN),
            new RefreshToken(ROTATED_REFRESH_TOKEN),
            ROTATED_SESSION_EXPIRES_AT,
            ROTATION_AT);
    public static final Map<ProviderAccount, UUID> EXPECTED_USERS_AFTER_ROTATION =
            Map.of(AuthVerifyFixtures.ACCOUNT, USER_ID);
    public static final Map<UUID, Session> EXPECTED_ROWS_AFTER_ROTATION = Map.of(
            SESSION_ID,
            new Session(
                    SESSION_ID,
                    USER_ID,
                    new RefreshToken(ROTATED_REFRESH_TOKEN),
                    LOGIN_AT,
                    ROTATED_SESSION_EXPIRES_AT));
    public static final List<String> EXPECTED_REFRESH_CALL_NAMES = List.of(
            FakeSessionRepository.FIND_ACTIVE_BY_REFRESH_TOKEN,
            StubAccessTokenIssuer.ISSUE_ACCESS_TOKEN,
            FakeSessionRepository.ROTATE_REFRESH_TOKEN);

    private RefreshSessionData() {
    }
}
