package com.uwords.adapter.cache;

import com.uwords.domain.auth.challenge.Challenge;
import com.uwords.usecase.port.auth.challenge.ChallengeStorePort;
import com.uwords.usecase.port.auth.challenge.CooldownAcquisition;
import java.util.List;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.data.redis.core.script.RedisScript;
import org.springframework.stereotype.Component;

@Component
public class RedisChallengeStore implements ChallengeStorePort {

    private static final long MINIMUM_RETRY_AFTER_SECONDS = 1;
    private static final double MILLISECONDS_IN_SECOND = 1000.0;
    private static final int ACQUIRED_FLAG_INDEX = 0;
    private static final int REMAINING_MILLISECONDS_INDEX = 1;
    private static final long ACQUIRED = 1;

    private static final RedisScript<List> ACQUIRE_COOLDOWN =
            RedisScript.of(CacheScripts.ACQUIRE_COOLDOWN, List.class);
    private static final RedisScript<Long> SWAP_CHALLENGE =
            RedisScript.of(CacheScripts.SWAP_CHALLENGE, Long.class);
    private static final RedisScript<Long> DISCARD_STARTED_CHALLENGE =
            RedisScript.of(CacheScripts.DISCARD_STARTED_CHALLENGE, Long.class);

    private final StringRedisTemplate client;

    public RedisChallengeStore(StringRedisTemplate client) {
        this.client = client;
    }

    @Override
    public CooldownAcquisition acquireCooldown(String challengeType, String uniquenessKey, long cooldownSeconds) {
        List<?> response = client.execute(
                ACQUIRE_COOLDOWN,
                List.of(CacheKeys.cooldownKey(challengeType, uniquenessKey)),
                String.valueOf(cooldownSeconds));
        if (numberAt(response, ACQUIRED_FLAG_INDEX) == ACQUIRED) {
            return CooldownAcquisition.granted();
        }
        return CooldownAcquisition.denied(retryAfterSeconds(numberAt(response, REMAINING_MILLISECONDS_INDEX)));
    }

    @Override
    public void swapChallenge(Challenge challenge) {
        client.execute(
                SWAP_CHALLENGE,
                List.of(CacheKeys.recordKey(challenge.id()), pointerKey(challenge)),
                ChallengeRecordCodec.encode(challenge),
                challenge.id().toString(),
                String.valueOf(challenge.ttlSeconds()),
                IsoOffsetText.of(challenge.createdAt()));
    }

    @Override
    public void discardStartedChallenge(Challenge challenge) {
        client.execute(
                DISCARD_STARTED_CHALLENGE,
                List.of(
                        CacheKeys.recordKey(challenge.id()),
                        pointerKey(challenge),
                        CacheKeys.cooldownKey(challenge.challengeType().value(), challenge.uniquenessKey())),
                challenge.id().toString());
    }

    private long retryAfterSeconds(long remainingMilliseconds) {
        long wholeSeconds = (long) Math.ceil(remainingMilliseconds / MILLISECONDS_IN_SECOND);
        return Math.max(wholeSeconds, MINIMUM_RETRY_AFTER_SECONDS);
    }

    private long numberAt(List<?> response, int index) {
        return ((Number) response.get(index)).longValue();
    }

    private String pointerKey(Challenge challenge) {
        return CacheKeys.pointerKey(challenge.challengeType().value(), challenge.uniquenessKey());
    }
}
