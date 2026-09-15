package com.uwords.usecase.port.auth.challenge;

import com.uwords.domain.auth.challenge.ChallengeVerification;
import java.util.Optional;
import java.util.UUID;

public interface ChallengeVerificationStorePort {

    Optional<StoredChallenge> findChallenge(UUID challengeId);

    ChallengeClaim claimAttempt(UUID challengeId, int maxAttempts);

    boolean redeemChallenge(UUID challengeId);

    void rememberVerification(ChallengeVerification verification, long ttlSeconds);

    Optional<ChallengeVerification> findVerification(UUID challengeId);
}
