package com.uwords.adapter.rest;

import com.uwords.adapter.rest.testing.VerifyChallengeStatements;
import org.junit.jupiter.api.Test;

class AuthChallengeVerifyControllerTest {

    private final VerifyChallengeStatements statements = new VerifyChallengeStatements();

    @Test
    void shouldAnswer200WithOnlyTheUserAndSessionFields() throws Exception {
        statements.givenUsecaseVerifiesTheCode();

        statements.whenClientSubmitsTheCode();

        statements.assertSessionIsAnsweredWithOnlyItsOwnFields();
    }

    @Test
    void shouldTranslateTheBodyIntoTheUsecaseRequest() throws Exception {
        statements.givenUsecaseVerifiesTheCode();

        statements.whenClientSubmitsTheCode();

        statements.assertUsecaseReceivedTheTranslatedRequest();
    }

    @Test
    void shouldIgnoreUnknownFieldsInTheBody() throws Exception {
        statements.givenUsecaseVerifiesTheCode();

        statements.whenClientSubmitsTheCodeWithUnknownFields();

        statements.assertUsecaseReceivedTheTranslatedRequest();
        statements.assertSessionIsAnsweredWithOnlyItsOwnFields();
    }
}
