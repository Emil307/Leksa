package com.uwords.usecase.service.auth;

import com.uwords.domain.auth.challenge.Challenge;
import com.uwords.domain.auth.challenge.ChallengeType;
import java.time.Instant;
import java.util.UUID;

public record StartedChallenge(UUID challengeId, ChallengeType challengeType, Instant expiresAt) {

    public static StartedChallenge of(Challenge challenge) {
        return new StartedChallenge(challenge.id(), challenge.challengeType(), challenge.expiresAt());
    }
}
