package com.uwords.application.testing.statements;

import static com.uwords.application.testing.statements.AccessTokenData.API_AUDIENCE;
import static com.uwords.application.testing.statements.AccessTokenData.LONG_PAST_EXPIRY;
import static com.uwords.application.testing.statements.AccessTokenData.claimsOf;
import static com.uwords.application.testing.statements.AccessTokenData.signed;

public final class ApplicationBootData {

    public static final String HEALTH_PATH = "/health";
    public static final String CHALLENGE_START_PATH = "/api/v1/auth/challenge/start";
    public static final String CHALLENGE_VERIFY_PATH = "/api/v1/auth/challenge/verify";
    public static final String PROFILE_PATH = "/api/v1/profile";

    public static final String JWT_SECRET_PROPERTY = "auth.token.jwt-secret";
    public static final String BLANK_SECRET = "";

    public static final String AUTHORIZATION_HEADER = "Authorization";
    public static final String UNAUTHORIZED_BODY =
            "{\"code\":\"UNAUTHORIZED\",\"message\":\"Unauthorized\",\"payload\":null}";

    private ApplicationBootData() {
    }

    public static String expiredBearerHeader() {
        return "Bearer " + signed(claimsOf(LONG_PAST_EXPIRY, API_AUDIENCE));
    }
}
