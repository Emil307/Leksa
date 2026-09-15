package com.uwords.usecase.service.auth;

import com.uwords.usecase.testing.statements.VerifyChallengeStatements;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class VerifyChallengeIssuesSessionTest {

    private VerifyChallengeStatements statements;

    @BeforeEach
    void createStatements() {
        statements = new VerifyChallengeStatements();
    }

    @Test
    void shouldAnswerWithTheExistingUserAndCreateNoOther() {
        statements.givenRegisteredUserHoldsAFreshCode();

        statements.whenUserSendsTheCorrectCode();

        statements.assertSessionBelongsToTheExistingUser();
        statements.assertNoNewUserIsCreated();
    }

    @Test
    void shouldAnswerWithASessionCarryingBothTokens() {
        statements.givenRegisteredUserHoldsAFreshCode();

        statements.whenUserSendsTheCorrectCode();

        statements.assertSessionCarriesItsOwnIdentityAndTokens();
        statements.assertAccessTokenIsIssuedForThatUserAndSession();
    }

    @Test
    void shouldClaimTheAttemptRedeemTheChallengeAndRememberTheVerification() {
        statements.givenRegisteredUserHoldsAFreshCode();

        statements.whenUserSendsTheCorrectCode();

        statements.assertAttemptIsClaimedBeforeTheChallengeIsRedeemed();
        statements.assertRedeemedChallengeIsRememberedForReplay();
    }
}
