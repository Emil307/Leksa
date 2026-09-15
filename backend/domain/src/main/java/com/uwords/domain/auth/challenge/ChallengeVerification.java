package com.uwords.domain.auth.challenge;

import java.util.UUID;

public record ChallengeVerification(UUID challengeId, UUID userId, UUID sessionId) {
}
