package com.uwords.e2e.stub;

import java.time.Instant;

public record IssuedChallenge(String challengeId, String email, String code, Instant issuedAt, Instant expiresAt) {
}
