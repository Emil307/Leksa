package com.uwords.usecase.testing.fakes;

import com.uwords.domain.auth.challenge.Challenge;
import com.uwords.domain.auth.challenge.ChallengeVerification;
import com.uwords.usecase.port.auth.challenge.ChallengeClaim;
import com.uwords.usecase.port.auth.challenge.ChallengeVerificationStorePort;
import com.uwords.usecase.port.auth.challenge.StoredChallenge;
import com.uwords.usecase.testing.recording.CallJournal;
import com.uwords.usecase.testing.recording.ClaimArguments;
import com.uwords.usecase.testing.recording.RememberedVerification;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;

public class FakeChallengeVerificationStore extends FakeChallengeStore
        implements ChallengeVerificationStorePort {

    public static final String FIND_CHALLENGE = "find_challenge";
    public static final String CLAIM_ATTEMPT = "claim_attempt";
    public static final String REDEEM_CHALLENGE = "redeem_challenge";
    public static final String REMEMBER_VERIFICATION = "remember_verification";
    public static final String FIND_VERIFICATION = "find_verification";

    public final Map<UUID, StoredChallenge> records = new LinkedHashMap<>();
    public final Map<UUID, ChallengeVerification> verifications = new LinkedHashMap<>();

    public FakeChallengeVerificationStore(CallJournal journal) {
        super(journal);
    }

    @Override
    public void swapChallenge(Challenge challenge) {
        super.swapChallenge(challenge);
        StoredChallenge stored = stored(challenge);
        records.values().removeIf(record -> record.uniquenessKey().equals(stored.uniquenessKey()));
        records.put(stored.id(), stored);
    }

    @Override
    public void discardStartedChallenge(Challenge challenge) {
        super.discardStartedChallenge(challenge);
        records.remove(challenge.id());
    }

    @Override
    public Optional<StoredChallenge> findChallenge(UUID challengeId) {
        journal.record(FIND_CHALLENGE, challengeId);
        return Optional.ofNullable(records.get(challengeId));
    }

    @Override
    public ChallengeClaim claimAttempt(UUID challengeId, int maxAttempts) {
        journal.record(CLAIM_ATTEMPT, new ClaimArguments(challengeId, maxAttempts));
        StoredChallenge stored = records.get(challengeId);
        if (stored == null) {
            return ChallengeClaim.missing();
        }
        StoredChallenge claimed = withNextAttempt(stored);
        if (claimed.attempts() >= maxAttempts) {
            records.remove(challengeId);
            return ChallengeClaim.exhaustedNow();
        }
        records.put(challengeId, claimed);
        return ChallengeClaim.of(claimed);
    }

    @Override
    public boolean redeemChallenge(UUID challengeId) {
        journal.record(REDEEM_CHALLENGE, challengeId);
        return records.remove(challengeId) != null;
    }

    @Override
    public void rememberVerification(ChallengeVerification verification, long ttlSeconds) {
        journal.record(REMEMBER_VERIFICATION, new RememberedVerification(verification, ttlSeconds));
        verifications.put(verification.challengeId(), verification);
    }

    @Override
    public Optional<ChallengeVerification> findVerification(UUID challengeId) {
        journal.record(FIND_VERIFICATION, challengeId);
        return Optional.ofNullable(verifications.get(challengeId));
    }

    private static StoredChallenge stored(Challenge challenge) {
        return new StoredChallenge(
                challenge.id(),
                challenge.challengeType(),
                challenge.uniquenessKey(),
                challenge.secretValue(),
                challenge.createdAt(),
                challenge.expiresAt(),
                challenge.attempts());
    }

    private static StoredChallenge withNextAttempt(StoredChallenge stored) {
        return new StoredChallenge(
                stored.id(),
                stored.challengeType(),
                stored.uniquenessKey(),
                stored.secretValue(),
                stored.createdAt(),
                stored.expiresAt(),
                stored.attempts() + 1);
    }
}
