package com.uwords.usecase.testing.recording;

import com.uwords.domain.auth.challenge.ChallengeVerification;

public record RememberedVerification(ChallengeVerification verification, long ttlSeconds) {
}
