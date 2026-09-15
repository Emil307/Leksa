package com.uwords.usecase.service.auth;

import com.uwords.usecase.testing.statements.StartChallengeStatements;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class StartChallengeQueuesRequestTest {

    private StartChallengeStatements statements;

    @BeforeEach
    void createStatements() {
        statements = new StartChallengeStatements();
    }

    @Test
    void shouldAnswerWithChallengeIdentityAndExpiry() {
        statements.whenClientRequestsCodeToOwnEmail();

        statements.assertStartedChallengeCarriesIdentityAndExpiry();
    }

    @Test
    void shouldQueueOneReadyRequestCarryingTheChallengeCode() {
        statements.whenClientRequestsCodeToOwnEmail();

        statements.assertExactlyOneReadyRequestIsQueued();
        statements.assertQueuedCodeIsTheIssuedChallengeSecret();
    }

    @Test
    void shouldQueueTheRequestOnlyAfterTheChallengeIsStored() {
        statements.whenClientRequestsCodeToOwnEmail();

        statements.assertRequestIsQueuedOnlyAfterChallengeIsStored();
    }

    @Test
    void shouldDiscardTheChallengeAndRefuseWhenTheQueueRejects() {
        statements.givenNotificationQueueRejectsRequests();

        statements.whenClientRequestsCodeAndStartFails();

        statements.assertStartIsRefusedAsUnavailable();
        statements.assertStartedChallengeIsDiscarded();
        statements.assertNoRequestIsQueued();
    }
}
