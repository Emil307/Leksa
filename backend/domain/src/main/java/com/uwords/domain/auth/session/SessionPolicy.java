package com.uwords.domain.auth.session;

import com.uwords.domain.common.ValidationException;
import java.time.Instant;
import java.time.temporal.ChronoUnit;

public record SessionPolicy(long accessTokenTtlSeconds, long refreshTokenTtlSeconds) {

    public static final String POSITIVE_TTL_MESSAGE = "Session token lifetimes must be positive";

    public static SessionPolicy of(long accessTokenTtlSeconds, long refreshTokenTtlSeconds) {
        if (accessTokenTtlSeconds <= 0 || refreshTokenTtlSeconds <= 0) {
            throw new ValidationException(POSITIVE_TTL_MESSAGE);
        }
        return new SessionPolicy(accessTokenTtlSeconds, refreshTokenTtlSeconds);
    }

    public Instant accessExpiryAt(Instant now) {
        return truncate(now).plusSeconds(accessTokenTtlSeconds);
    }

    public Instant refreshExpiryAt(Instant now) {
        return truncate(now).plusSeconds(refreshTokenTtlSeconds);
    }

    public static Instant truncate(Instant now) {
        return now.truncatedTo(ChronoUnit.SECONDS);
    }
}
