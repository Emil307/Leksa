package com.uwords.adapter.rest;

import com.uwords.adapter.rest.testing.ProfileStatements;
import org.junit.jupiter.api.Test;

class ProfileControllerTest {

    private final ProfileStatements statements = new ProfileStatements();

    @Test
    void shouldAnswer200WithTheWholeAccountAtTheBodyRoot() throws Exception {
        statements.givenAccountWithEveryFieldFilled();

        statements.whenTheProfileIsRequested();

        statements.assertAnsweredTheWholeAccountAtTheBodyRoot();
    }

    @Test
    void shouldRenderUnsetColumnsAsPresentJsonNulls() throws Exception {
        statements.givenAccountWithOnlyTheRequiredColumns();

        statements.whenTheProfileIsRequested();

        statements.assertAnsweredTheAccountWithUnsetColumnsAsJsonNulls();
    }

    @Test
    void shouldPassTheRawAuthorizationHeaderToTheAuthenticateService() throws Exception {
        statements.givenAccountWithEveryFieldFilled();

        statements.whenTheProfileIsRequested();

        statements.assertTheRawAuthorizationHeaderReachedTheGuard();
    }

    @Test
    void shouldPassNullWhenTheAuthorizationHeaderIsAbsent() throws Exception {
        statements.givenAccountWithEveryFieldFilled();
        statements.givenNoAuthorizationHeader();

        statements.whenTheProfileIsRequested();

        statements.assertTheAbsentAuthorizationHeaderReachedTheGuardAsNull();
    }

    @Test
    void shouldSelectTheAccountOfTheAuthenticatedCallerOnly() throws Exception {
        statements.givenAccountWithEveryFieldFilled();
        statements.givenAForeignUserIdInTheQuery();

        statements.whenTheProfileIsRequested();

        statements.assertAnsweredTheAuthenticatedCallersAccountOnly();
    }

    @Test
    void shouldAnswerTheUniform401WhenTheGuardRefusesTheRequest() throws Exception {
        statements.givenAccountWithEveryFieldFilled();
        statements.givenTheGuardRefusesTheRequest();

        statements.whenTheProfileIsRequested();

        statements.assertAnsweredTheUniform401WithoutReadingAnyAccount();
    }
}
