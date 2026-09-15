package com.uwords.domain.auth.challenge;

import java.time.Duration;
import java.time.Instant;

public record ChallengePolicy(
        long ttlSeconds,
        int maxAttempts,
        long resendCooldownSeconds,
        long replayWindowSeconds) {

    public long replayTtlSeconds(Instant now, Instant expiresAt) {
        Duration remaining = Duration.between(now, expiresAt);
        long truncated = remaining.getSeconds();
        if (truncated < 0 && remaining.getNano() > 0) {
            truncated += 1;
        }
        return Math.min(replayWindowSeconds, truncated);
    }
}
