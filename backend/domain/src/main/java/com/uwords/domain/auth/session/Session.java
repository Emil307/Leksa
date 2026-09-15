package com.uwords.domain.auth.session;

import java.time.Instant;
import java.util.UUID;

public record Session(
        UUID id,
        UUID userId,
        RefreshToken refreshToken,
        Instant createdAt,
        Instant expiresAt) {

    public boolean isExpiredAt(Instant now) {
        return !expiresAt.isAfter(now);
    }

    public Session rotate(RefreshToken newToken, Instant now, SessionPolicy policy) {
        return rotatedTo(newToken, policy.refreshExpiryAt(now));
    }

    public Session rotatedTo(RefreshToken newToken, Instant newExpiresAt) {
        return new Session(id, userId, newToken, createdAt, newExpiresAt);
    }

    public AccessTokenClaims accessTokenClaims(UUID tokenId, Instant now, SessionPolicy policy) {
        return AccessTokenClaims.of(userId, id, tokenId, now, policy);
    }
}
