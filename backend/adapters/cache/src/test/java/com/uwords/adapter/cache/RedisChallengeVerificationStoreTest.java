package com.uwords.adapter.cache;

import com.uwords.adapter.cache.testing.statements.VerificationStoreStatements;
import java.util.List;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class RedisChallengeVerificationStoreTest {

    private VerificationStoreStatements statements;

    @BeforeEach
    void createStatements() {
        statements = new VerificationStoreStatements();
    }

    @AfterEach
    void closeStatements() {
        statements.close();
    }

    @Test
    void shouldReadTheRecordWrittenByTheChallengeStore() {
        statements.givenStartedChallenge();

        statements.findChallenge();

        statements.assertFoundChallengeIsTheStartedRecord();
    }

    @Test
    void shouldFindNothingForAnUnknownChallenge() {
        statements.givenNoStartedChallenge();

        statements.findChallenge();

        statements.assertNoChallengeFound();
    }

    @Test
    void shouldReturnTheFreshlyIncrementedRecordOnEveryClaim() {
        statements.givenStartedChallenge();

        statements.claimAttempt(2);

        statements.assertClaimsReturnedGrowingAttempts(List.of(1, 2));
    }

    @Test
    void shouldDropRecordAndPointerWhenTheLastAttemptIsClaimed() {
        statements.givenStartedChallenge();

        statements.claimAttempt(3);

        statements.assertLastClaimReportsExhaustedNow();
        statements.assertRecordAndPointerAreGone();
    }

    @Test
    void shouldReportMissingWhenClaimingAnUnknownChallenge() {
        statements.givenNoStartedChallenge();

        statements.claimAttempt();

        statements.assertLastClaimReportsMissing();
    }

    @Test
    void shouldRedeemTheChallengeForTheFirstCallerOnly() {
        statements.givenStartedChallenge();

        statements.redeemChallenge(2);

        statements.assertOnlyTheFirstRedemptionWon();
        statements.assertRecordIsGone();
    }

    @Test
    void shouldRememberTheVerificationUnderTheRedeemedChallengeWithItsTtl() {
        statements.givenNoRememberedVerification();

        statements.rememberVerification();
        statements.findVerification();

        statements.assertFoundVerificationIsTheRememberedOne();
        statements.assertVerificationExpiresWithinTheGivenTtl();
    }

    @Test
    void shouldFindNothingOnceTheRememberedVerificationIsGone() {
        statements.givenNoRememberedVerification();

        statements.findVerification();

        statements.assertNoVerificationFound();
    }
}
