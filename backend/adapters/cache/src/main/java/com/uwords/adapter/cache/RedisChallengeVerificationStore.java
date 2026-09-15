package com.uwords.adapter.cache;

import com.uwords.domain.auth.challenge.ChallengeVerification;
import com.uwords.usecase.port.auth.challenge.ChallengeClaim;
import com.uwords.usecase.port.auth.challenge.ChallengeVerificationStorePort;
import com.uwords.usecase.port.auth.challenge.StoredChallenge;
import java.time.Duration;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.data.redis.core.script.RedisScript;
import org.springframework.stereotype.Component;

@Component
public class RedisChallengeVerificationStore implements ChallengeVerificationStorePort {

    public static final String CLAIMED_STATUS = "claimed";
    public static final String EXHAUSTED_STATUS = "exhausted";

    private static final int STATUS_INDEX = 0;
    private static final int RECORD_INDEX = 1;

    private static final RedisScript<List> CLAIM_ATTEMPT = RedisScript.of(CacheScripts.CLAIM_ATTEMPT, List.class);

    private final StringRedisTemplate client;

    public RedisChallengeVerificationStore(StringRedisTemplate client) {
        this.client = client;
    }

    @Override
    public Optional<StoredChallenge> findChallenge(UUID challengeId) {
        return Optional.ofNullable(client.opsForValue().get(CacheKeys.recordKey(challengeId)))
                .map(ChallengeRecordCodec::decode);
    }

    @Override
    public ChallengeClaim claimAttempt(UUID challengeId, int maxAttempts) {
        List<?> response = client.execute(
                CLAIM_ATTEMPT,
                List.of(CacheKeys.recordKey(challengeId)),
                String.valueOf(maxAttempts));
        return claimOf(response);
    }

    @Override
    public boolean redeemChallenge(UUID challengeId) {
        return Boolean.TRUE.equals(client.delete(CacheKeys.recordKey(challengeId)));
    }

    @Override
    public void rememberVerification(ChallengeVerification verification, long ttlSeconds) {
        client.opsForValue().set(
                CacheKeys.verificationKey(verification.challengeId()),
                VerificationRecordCodec.encode(verification),
                Duration.ofSeconds(ttlSeconds));
    }

    @Override
    public Optional<ChallengeVerification> findVerification(UUID challengeId) {
        return Optional.ofNullable(client.opsForValue().get(CacheKeys.verificationKey(challengeId)))
                .map(VerificationRecordCodec::decode);
    }

    private ChallengeClaim claimOf(List<?> response) {
        String status = String.valueOf(response.get(STATUS_INDEX));
        return switch (status) {
            case EXHAUSTED_STATUS -> ChallengeClaim.exhaustedNow();
            case CLAIMED_STATUS -> ChallengeClaim.of(
                    ChallengeRecordCodec.decode(String.valueOf(response.get(RECORD_INDEX))));
            default -> ChallengeClaim.missing();
        };
    }
}
