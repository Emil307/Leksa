package com.uwords.adapter.rest;

import com.uwords.adapter.rest.testing.ExceptionHandlerStatements;
import org.junit.jupiter.api.Test;

class GlobalExceptionHandlerTest {

    private final ExceptionHandlerStatements statements = new ExceptionHandlerStatements();

    @Test
    void shouldMapNotFoundTo404WithCodeAndMessage() throws Exception {
        statements.givenTheRouteRaisesANotFoundCarryingAPayload();

        statements.whenTheRouteIsCalled();

        statements.assertAnswered404WithTheCodeMessageAndPayload();
    }

    @Test
    void shouldHideMessageWhenNotExposedToUser() throws Exception {
        statements.givenTheRouteRaisesAConflictHiddenFromTheUser();

        statements.whenTheRouteIsCalled();

        statements.assertAnswered409WithoutTheInternalMessageOrPayload();
    }

    @Test
    void shouldAnswerTheUniform401BodyForEveryRefusalReason() throws Exception {
        statements.assertEveryRefusalReasonAnswersTheUniform401();
    }

    @Test
    void shouldRecordTheRefusalReasonInTheLogInsteadOfTheResponse() throws Exception {
        statements.givenTheRouteRefusesASessionRowWithoutARecordedLifetime();

        statements.whenTheRouteIsCalledWhileLogsAreCaptured();

        statements.assertTheReasonIsLoggedAndAbsentFromTheResponse();
    }
}
