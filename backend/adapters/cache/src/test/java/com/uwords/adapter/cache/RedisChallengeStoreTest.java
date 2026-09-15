package com.uwords.adapter.cache;

import com.uwords.adapter.cache.testing.statements.ChallengeStoreStatements;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class RedisChallengeStoreTest {

    private ChallengeStoreStatements statements;

    @BeforeEach
    void createStatements() {
        statements = new ChallengeStoreStatements();
    }

    @Test
    void shouldAcquireCooldownWhenItIsFree() {
        statements.givenCooldownFree();

        statements.acquireCooldown();

        statements.assertCooldownAcquired();
        statements.assertSingleCooldownScriptOverCooldownKey();
    }

    @Test
    void shouldReportRetryAfterRoundedUpWhenCooldownIsHeld() {
        statements.givenCooldownHeldWithPartialSecondLeft();

        statements.acquireCooldown();

        statements.assertCooldownDeniedRoundingUp();
        statements.assertSingleCooldownScriptOverCooldownKey();
    }

    @Test
    void shouldNeverReportRetryAfterBelowOneSecond() {
        statements.givenCooldownHeldWithLessThanASecondLeft();

        statements.acquireCooldown();

        statements.assertCooldownDeniedWithOneSecondFloor();
        statements.assertSingleCooldownScriptOverCooldownKey();
    }

    @Test
    void shouldSwapRecordAndPointerAtomicallyWithChallengeTtl() {
        statements.givenRedisAppliesTheScript();

        statements.swapChallenge();

        statements.assertSingleSwapScriptOverRecordAndPointer();
    }

    @Test
    void shouldNotWriteAgainWhenSwapIsRefusedByANewerRecord() {
        statements.givenRedisRefusesTheSwapForANewerRecord();

        statements.swapChallenge();

        statements.assertSingleSwapScriptOverRecordAndPointer();
        statements.assertSwapRefusalIsSilentAndWritesNothingFurther();
    }

    @Test
    void shouldDiscardRecordPointerAndCooldownOwnedByTheChallenge() {
        statements.givenRedisAppliesTheScript();

        statements.discardStartedChallenge();

        statements.assertSingleDiscardScriptOverAllOwnedKeys();
    }
}
