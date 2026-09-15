package com.uwords.adapter.rest;

import com.uwords.adapter.rest.testing.RefreshLogRedactionStatements;
import org.junit.jupiter.api.Test;

class AuthTokenControllerLogRedactionTest {

    private final RefreshLogRedactionStatements statements = new RefreshLogRedactionStatements();

    @Test
    void shouldKeepThePresentedTokenOutOfTheLogsWhenValidationRefusesIt() throws Exception {
        statements.givenTheUsecaseRefusesTheTokenAsInvalid();

        statements.whenTheClientRefreshesWhileAllLogsAreCaptured();

        statements.assertTheRefusalWasAnsweredWith(400);
        statements.assertNoLogLineCarriesTheToken();
    }

    @Test
    void shouldKeepThePresentedTokenOutOfTheLogsWhenTheSessionIsRefused() throws Exception {
        statements.givenTheUsecaseRefusesTheSession();

        statements.whenTheClientRefreshesWhileAllLogsAreCaptured();

        statements.assertTheRefusalWasAnsweredWith(401);
        statements.assertNoLogLineCarriesTheToken();
    }

    @Test
    void shouldKeepThePresentedTokenOutOfTheLogsWhenTheBodyIsUnreadable() throws Exception {
        statements.givenTheBodyIsTruncatedAfterTheToken();

        statements.whenTheClientRefreshesWhileAllLogsAreCaptured();

        statements.assertTheRefusalWasAnsweredWith(400);
        statements.assertNoLogLineCarriesTheToken();
    }
}
