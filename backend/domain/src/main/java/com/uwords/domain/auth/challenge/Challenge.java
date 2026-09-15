package com.uwords.domain.auth.challenge;

import java.time.Duration;
import java.time.Instant;
import java.util.UUID;

public record Challenge(
        UUID id,
        ChallengeType challengeType,
        String uniquenessKey,
        ChallengeSecret secret,
        Instant createdAt,
        Instant expiresAt,
        int attempts) {

    public static Challenge create(
            UUID challengeId,
            ChallengeType challengeType,
            ChallengeSubject subject,
            ChallengeSecret secret,
            Instant now,
            ChallengePolicy policy) {
        return new Challenge(
                challengeId,
                challengeType,
                subject.uniquenessKey(),
                secret,
                now,
                now.plusSeconds(policy.ttlSeconds()),
                0);
    }

    public long ttlSeconds() {
        Duration lifetime = Duration.between(createdAt, expiresAt);
        long seconds = lifetime.getSeconds();
        return lifetime.getNano() > 0 ? seconds + 1 : seconds;
    }

    public String secretValue() {
        return secret.value();
    }
}
