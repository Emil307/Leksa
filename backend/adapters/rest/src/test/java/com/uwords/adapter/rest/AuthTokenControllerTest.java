package com.uwords.adapter.rest;

import com.uwords.adapter.rest.testing.RefreshSessionStatements;
import org.junit.jupiter.api.Test;

class AuthTokenControllerTest {

    private final RefreshSessionStatements statements = new RefreshSessionStatements();

    @Test
    void shouldAnswer200WithOnlyTheRotatedSessionFields() throws Exception {
        statements.givenUsecaseRotatesTheSession();

        statements.whenClientRefreshesTheTokens();

        statements.assertRotatedSessionIsAnsweredWithOnlyItsOwnFields();
    }

    @Test
    void shouldTranslateTheBodyIntoTheUsecaseRequest() throws Exception {
        statements.givenUsecaseRotatesTheSession();

        statements.whenClientRefreshesTheTokens();

        statements.assertUsecaseReceivedTheTranslatedRequest();
    }
}
