package com.uwords.domain.auth.session;

import java.time.Instant;
import java.util.UUID;

public record AccessTokenClaims(UUID subject, UUID sessionId, UUID tokenId, Instant expiresAt) {

    public static AccessTokenClaims of(
            UUID subject, UUID sessionId, UUID tokenId, Instant now, SessionPolicy policy) {
        return new AccessTokenClaims(subject, sessionId, tokenId, policy.accessExpiryAt(now));
    }
}
