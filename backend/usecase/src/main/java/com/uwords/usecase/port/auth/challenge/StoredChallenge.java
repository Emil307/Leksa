package com.uwords.usecase.port.auth.challenge;

import com.uwords.domain.auth.challenge.ChallengeType;
import java.time.Instant;
import java.util.UUID;

public record StoredChallenge(
        UUID id,
        ChallengeType challengeType,
        String uniquenessKey,
        String secretValue,
        Instant createdAt,
        Instant expiresAt,
        int attempts) {

    @Override
    public String toString() {
        return "StoredChallenge(id=" + id
                + ", challengeType=" + challengeType
                + ", secretValue=<redacted>)";
    }
}
