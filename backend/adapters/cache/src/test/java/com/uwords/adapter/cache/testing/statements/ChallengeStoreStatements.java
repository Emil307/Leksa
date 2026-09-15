package com.uwords.adapter.cache.testing.statements;

import static org.assertj.core.api.Assertions.assertThat;

import com.uwords.adapter.cache.CacheScripts;
import com.uwords.adapter.cache.RedisChallengeStore;
import com.uwords.adapter.cache.testing.fakes.EvalCall;
import com.uwords.adapter.cache.testing.fakes.FakeStringRedisTemplate;
import com.uwords.domain.auth.challenge.Challenge;
import com.uwords.domain.auth.challenge.ChallengeType;
import com.uwords.domain.auth.code.VerificationCode;
import com.uwords.usecase.port.auth.challenge.CooldownAcquisition;
import java.time.Instant;
import java.util.List;
import java.util.UUID;

public class ChallengeStoreStatements {

    public static final String CHALLENGE_ID_TEXT = "11111111-1111-4111-8111-111111111111";
    public static final String UNIQUENESS_KEY = "user@example.com";
    public static final String CHALLENGE_TYPE = "EMAIL_CODE";
    public static final String CODE = "0042";
    public static final String CREATED_AT_TEXT = "2026-09-03T10:00:00+00:00";
    public static final String EXPIRES_AT_TEXT = "2026-09-03T10:05:00+00:00";
    public static final String TTL_SECONDS_TEXT = "300";
    public static final long COOLDOWN_SECONDS = 60;
    public static final String COOLDOWN_SECONDS_TEXT = "60";
    public static final String COOLDOWN_KEY_VALUE = "challenge:cooldown:EMAIL_CODE:user@example.com";
    public static final String RECORD_KEY_VALUE = "challenge:11111111-1111-4111-8111-111111111111";
    public static final String POINTER_KEY_VALUE = "challenge:key:EMAIL_CODE:user@example.com";
    public static final String EXPECTED_RECORD = "{\"id\": \"11111111-1111-4111-8111-111111111111\","
            + " \"challengeType\": \"EMAIL_CODE\", \"uniquenessKey\": \"user@example.com\","
            + " \"secret\": \"0042\", \"createdAt\": \"2026-09-03T10:00:00+00:00\","
            + " \"expiresAt\": \"2026-09-03T10:05:00+00:00\", \"attempts\": 0}";

    private final FakeStringRedisTemplate client = new FakeStringRedisTemplate();
    private final RedisChallengeStore store = new RedisChallengeStore(client);
    private final Challenge challenge = new Challenge(
            UUID.fromString(CHALLENGE_ID_TEXT),
            ChallengeType.EMAIL_CODE,
            UNIQUENESS_KEY,
            new VerificationCode(CODE),
            Instant.parse(CREATED_AT_TEXT),
            Instant.parse(EXPIRES_AT_TEXT),
            0);

    private CooldownAcquisition acquisition;

    public void givenCooldownFree() {
        client.willReturn(List.of(1L, 0L));
    }

    public void givenCooldownHeldWithPartialSecondLeft() {
        client.willReturn(List.of(0L, 1500L));
    }

    public void givenCooldownHeldWithLessThanASecondLeft() {
        client.willReturn(List.of(0L, 200L));
    }

    public void givenRedisAppliesTheScript() {
        client.willReturn(1L);
    }

    public void givenRedisRefusesTheSwapForANewerRecord() {
        client.willReturn(0L);
    }

    public void acquireCooldown() {
        acquisition = store.acquireCooldown(CHALLENGE_TYPE, UNIQUENESS_KEY, COOLDOWN_SECONDS);
    }

    public void swapChallenge() {
        store.swapChallenge(challenge);
    }

    public void discardStartedChallenge() {
        store.discardStartedChallenge(challenge);
    }

    public void assertCooldownAcquired() {
        assertThat(acquisition).isEqualTo(new CooldownAcquisition(true, 0));
    }

    public void assertCooldownDeniedRoundingUp() {
        assertThat(acquisition).isEqualTo(new CooldownAcquisition(false, 2));
    }

    public void assertCooldownDeniedWithOneSecondFloor() {
        assertThat(acquisition).isEqualTo(new CooldownAcquisition(false, 1));
    }

    public void assertSingleCooldownScriptOverCooldownKey() {
        EvalCall call = singleCall(CacheScripts.ACQUIRE_COOLDOWN);
        assertThat(call.keys()).isEqualTo(List.of(COOLDOWN_KEY_VALUE));
        assertThat(call.args()).isEqualTo(List.of(COOLDOWN_SECONDS_TEXT));
    }

    public void assertSingleSwapScriptOverRecordAndPointer() {
        EvalCall call = singleCall(CacheScripts.SWAP_CHALLENGE);
        assertThat(call.keys()).isEqualTo(List.of(RECORD_KEY_VALUE, POINTER_KEY_VALUE));
        assertThat(call.args()).isEqualTo(
                List.of(EXPECTED_RECORD, CHALLENGE_ID_TEXT, TTL_SECONDS_TEXT, CREATED_AT_TEXT));
    }

    public void assertSwapRefusalIsSilentAndWritesNothingFurther() {
        assertThat(client.calls().stream().map(EvalCall::script).toList())
                .isEqualTo(List.of(CacheScripts.SWAP_CHALLENGE));
    }

    public void assertSingleDiscardScriptOverAllOwnedKeys() {
        EvalCall call = singleCall(CacheScripts.DISCARD_STARTED_CHALLENGE);
        assertThat(call.keys()).isEqualTo(List.of(RECORD_KEY_VALUE, POINTER_KEY_VALUE, COOLDOWN_KEY_VALUE));
        assertThat(call.args()).isEqualTo(List.of(CHALLENGE_ID_TEXT));
    }

    private EvalCall singleCall(String script) {
        assertThat(client.calls()).hasSize(1);
        EvalCall call = client.calls().get(0);
        assertThat(call.script()).isEqualTo(script);
        return call;
    }
}
