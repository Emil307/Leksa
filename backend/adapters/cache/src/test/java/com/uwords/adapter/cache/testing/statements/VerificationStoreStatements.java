package com.uwords.adapter.cache.testing.statements;

import static org.assertj.core.api.Assertions.assertThat;

import com.uwords.adapter.cache.CacheKeys;
import com.uwords.adapter.cache.RedisChallengeStore;
import com.uwords.adapter.cache.RedisChallengeVerificationStore;
import com.uwords.adapter.cache.testing.LiveRedis;
import com.uwords.domain.auth.challenge.Challenge;
import com.uwords.domain.auth.challenge.ChallengeType;
import com.uwords.domain.auth.challenge.ChallengeVerification;
import com.uwords.domain.auth.code.VerificationCode;
import com.uwords.usecase.port.auth.challenge.ChallengeClaim;
import com.uwords.usecase.port.auth.challenge.StoredChallenge;
import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import java.util.concurrent.TimeUnit;
import org.springframework.data.redis.core.StringRedisTemplate;

public class VerificationStoreStatements {

    public static final String CODE = "0042";
    public static final long TTL_SECONDS = 300;
    public static final int MAX_ATTEMPTS = 3;
    public static final long VERIFICATION_TTL_SECONDS = 60;
    public static final long MILLISECONDS_IN_SECOND = 1000;

    private final StringRedisTemplate client = LiveRedis.template();
    private final RedisChallengeStore challengeStore = new RedisChallengeStore(client);
    private final RedisChallengeVerificationStore store = new RedisChallengeVerificationStore(client);
    private final UUID challengeId = UUID.randomUUID();
    private final String uniquenessKey = "user-" + challengeId + "@example.com";
    private final Instant createdAt = Instant.now().truncatedTo(ChronoUnit.MICROS);
    private final Challenge challenge = new Challenge(challengeId, ChallengeType.EMAIL_CODE, uniquenessKey,
            new VerificationCode(CODE), createdAt, createdAt.plusSeconds(TTL_SECONDS), 0);
    private final ChallengeVerification verification =
            new ChallengeVerification(challengeId, UUID.randomUUID(), UUID.randomUUID());
    private final List<ChallengeClaim> claims = new ArrayList<>();
    private final List<Boolean> redemptions = new ArrayList<>();

    private Optional<StoredChallenge> found = Optional.empty();
    private Optional<ChallengeVerification> foundVerification = Optional.empty();

    public void close() {
        client.delete(List.of(recordKey(), pointerKey(), verificationKey()));
    }

    public void givenStartedChallenge() {
        challengeStore.swapChallenge(challenge);
    }

    public void givenNoStartedChallenge() {
        client.delete(List.of(recordKey(), pointerKey()));
    }

    public void givenNoRememberedVerification() {
        client.delete(verificationKey());
    }

    public void findChallenge() {
        found = store.findChallenge(challengeId);
    }

    public void claimAttempt() {
        claimAttempt(1);
    }

    public void claimAttempt(int times) {
        for (int attempt = 0; attempt < times; attempt++) {
            claims.add(store.claimAttempt(challengeId, MAX_ATTEMPTS));
        }
    }

    public void redeemChallenge(int times) {
        for (int attempt = 0; attempt < times; attempt++) {
            redemptions.add(store.redeemChallenge(challengeId));
        }
    }

    public void rememberVerification() {
        store.rememberVerification(verification, VERIFICATION_TTL_SECONDS);
    }

    public void findVerification() {
        foundVerification = store.findVerification(challengeId);
    }

    public void assertFoundChallengeIsTheStartedRecord() {
        assertThat(found).isEqualTo(Optional.of(storedChallenge(0)));
    }

    public void assertNoChallengeFound() {
        assertThat(found).isEmpty();
    }

    public void assertClaimsReturnedGrowingAttempts(List<Integer> attempts) {
        assertThat(claims).isEqualTo(attempts.stream().map(each -> ChallengeClaim.of(storedChallenge(each))).toList());
    }

    public void assertLastClaimReportsExhaustedNow() {
        assertThat(claims.get(claims.size() - 1)).isEqualTo(ChallengeClaim.exhaustedNow());
    }

    public void assertLastClaimReportsMissing() {
        assertThat(claims.get(claims.size() - 1)).isEqualTo(ChallengeClaim.missing());
    }

    public void assertRecordAndPointerAreGone() {
        assertThat(client.countExistingKeys(List.of(recordKey(), pointerKey()))).isEqualTo(0);
    }

    public void assertRecordIsGone() {
        assertThat(client.countExistingKeys(List.of(recordKey()))).isEqualTo(0);
    }

    public void assertOnlyTheFirstRedemptionWon() {
        assertThat(redemptions).isEqualTo(List.of(true, false));
    }

    public void assertFoundVerificationIsTheRememberedOne() {
        assertThat(foundVerification).isEqualTo(Optional.of(verification));
    }

    public void assertNoVerificationFound() {
        assertThat(foundVerification).isEmpty();
    }

    public void assertVerificationExpiresWithinTheGivenTtl() {
        long expected = VERIFICATION_TTL_SECONDS * MILLISECONDS_IN_SECOND;
        assertThat(client.getExpire(verificationKey(), TimeUnit.MILLISECONDS))
                .isBetween(expected - MILLISECONDS_IN_SECOND, expected);
    }

    private StoredChallenge storedChallenge(int attempts) {
        return new StoredChallenge(challengeId, ChallengeType.EMAIL_CODE, uniquenessKey, CODE,
                createdAt, createdAt.plusSeconds(TTL_SECONDS), attempts);
    }

    private String recordKey() {
        return CacheKeys.recordKey(challengeId);
    }

    private String pointerKey() {
        return CacheKeys.pointerKey(ChallengeType.EMAIL_CODE.value(), uniquenessKey);
    }

    private String verificationKey() {
        return CacheKeys.verificationKey(challengeId);
    }
}
