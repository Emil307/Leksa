package com.uwords.domain.auth.session;

import java.time.Instant;
import java.util.UUID;

public record ActiveSession(UUID id, UUID userId, Instant expiresAt) {

    public boolean authorizes(VerifiedAccessToken token, Instant now) {
        return id.equals(token.sessionId())
                && userId.equals(token.subject())
                && now.isBefore(expiresAt);
    }
}
