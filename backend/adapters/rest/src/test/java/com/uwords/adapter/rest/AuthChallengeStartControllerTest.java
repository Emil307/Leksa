package com.uwords.adapter.rest;

import com.uwords.adapter.rest.testing.StartChallengeStatements;
import org.junit.jupiter.api.Test;

class AuthChallengeStartControllerTest {

    private final StartChallengeStatements statements = new StartChallengeStatements();

    @Test
    void shouldAnswer200WithOnlyTheChallengeFields() throws Exception {
        statements.givenUsecaseStartsTheChallenge();

        statements.whenClientRequestsACode();

        statements.assertChallengeIsAnsweredWithOnlyItsOwnFields();
    }

    @Test
    void shouldTranslateTheBodyIntoTheUsecaseRequest() throws Exception {
        statements.givenUsecaseStartsTheChallenge();

        statements.whenClientRequestsACode();

        statements.assertUsecaseReceivedTheTranslatedRequest();
    }

    @Test
    void shouldIgnoreServerOwnedFieldsInTheBody() throws Exception {
        statements.givenUsecaseStartsTheChallenge();

        statements.whenClientRequestsACodeWithServerOwnedFields();

        statements.assertUsecaseReceivedTheTranslatedRequest();
        statements.assertChallengeIsAnsweredWithOnlyItsOwnFields();
    }

    @Test
    void shouldLetTheDomainRejectABodyWithoutEmailAndType() throws Exception {
        statements.givenUsecaseRejectsTheCredentialAndType();

        statements.whenClientSendsABodyWithoutEmailAndType();

        statements.assertUsecaseReceivedAnEmptyCredentialAndType();
        statements.assertRequestIsRefusedAsInvalid();
    }

    @Test
    void shouldLetTheDomainRejectNullEmailAndType() throws Exception {
        statements.givenUsecaseRejectsTheCredentialAndType();

        statements.whenClientSendsNullEmailAndType();

        statements.assertUsecaseReceivedAnEmptyCredentialAndType();
        statements.assertRequestIsRefusedAsInvalid();
    }

    @Test
    void shouldLetTheDomainRejectEmptyEmailAndType() throws Exception {
        statements.givenUsecaseRejectsTheCredentialAndType();

        statements.whenClientSendsEmptyEmailAndType();

        statements.assertUsecaseReceivedAnEmptyCredentialAndType();
        statements.assertRequestIsRefusedAsInvalid();
    }

    @Test
    void shouldAnswer409WithRetryAfterSecondsWhenTheCooldownIsArmed() throws Exception {
        statements.givenUsecaseIsCoolingDown();

        statements.whenClientRequestsACode();

        statements.assertRequestIsRefusedAsCoolingDown();
    }

    @Test
    void shouldAnswer503WithoutLeakingDetailsWhenTheChallengeCannotBeAccepted() throws Exception {
        statements.givenUsecaseCannotAcceptTheChallenge();

        statements.whenClientRequestsACode();

        statements.assertRequestIsRefusedAsUnavailable();
    }
}
