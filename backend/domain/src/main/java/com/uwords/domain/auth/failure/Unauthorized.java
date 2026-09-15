package com.uwords.domain.auth.failure;

import com.uwords.domain.common.UnauthorizedException;
import java.util.Map;

public final class Unauthorized {

    public static final String UNAUTHORIZED_MESSAGE = "Unauthorized";
    private static final String REASON_KEY = "reason";

    private Unauthorized() {
    }

    public static UnauthorizedException of(AuthFailureReason reason) {
        return new UnauthorizedException(
                UNAUTHORIZED_MESSAGE,
                Map.of(REASON_KEY, reason.value()),
                false);
    }
}
