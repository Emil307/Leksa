package com.uwords.domain.auth.session;

import com.uwords.domain.auth.failure.AuthFailureReason;
import com.uwords.domain.auth.failure.Unauthorized;
import com.uwords.domain.common.UuidText;
import java.time.Instant;
import java.util.Map;
import java.util.UUID;

public record VerifiedAccessToken(UUID subject, UUID sessionId, UUID tokenId, Instant expiresAt) {

    public static final String API_AUDIENCE = "uwords-api";
    public static final long MIN_EXPIRY_SECONDS = 1;
    public static final long MAX_EXPIRY_SECONDS = 253402300799L;

    public static final String SUBJECT_CLAIM = "sub";
    public static final String SESSION_CLAIM = "sid";
    public static final String TOKEN_ID_CLAIM = "jti";
    public static final String EXPIRY_CLAIM = "exp";
    public static final String AUDIENCE_CLAIM = "aud";

    public static VerifiedAccessToken of(Map<String, Object> claims) {
        requireApiAudience(claims.get(AUDIENCE_CLAIM));
        return new VerifiedAccessToken(
                readUuid(claims.get(SUBJECT_CLAIM)),
                readUuid(claims.get(SESSION_CLAIM)),
                readUuid(claims.get(TOKEN_ID_CLAIM)),
                readExpiry(claims.get(EXPIRY_CLAIM)));
    }

    public boolean isExpiredAt(Instant now) {
        return !now.isBefore(expiresAt);
    }

    private static void requireApiAudience(Object value) {
        if (!API_AUDIENCE.equals(value)) {
            throw Unauthorized.of(AuthFailureReason.CLAIMS);
        }
    }

    private static UUID readUuid(Object value) {
        return switch (value) {
            case String text -> UuidText.parse(text)
                    .orElseThrow(() -> Unauthorized.of(AuthFailureReason.CLAIMS));
            case null, default -> throw Unauthorized.of(AuthFailureReason.CLAIMS);
        };
    }

    private static Instant readExpiry(Object value) {
        return switch (value) {
            case Integer number -> fromEpochSeconds(number.longValue());
            case Long number -> fromEpochSeconds(number);
            case null, default -> throw Unauthorized.of(AuthFailureReason.CLAIMS);
        };
    }

    private static Instant fromEpochSeconds(long seconds) {
        if (seconds < MIN_EXPIRY_SECONDS || seconds > MAX_EXPIRY_SECONDS) {
            throw Unauthorized.of(AuthFailureReason.CLAIMS);
        }
        return Instant.ofEpochSecond(seconds);
    }
}
