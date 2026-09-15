package com.uwords.adapter.rest;

import com.uwords.adapter.rest.testing.HealthStatements;
import org.junit.jupiter.api.Test;

class HealthControllerTest {

    private final HealthStatements statements = new HealthStatements();

    @Test
    void shouldAnswer200UpWhenTheApplicationIsReady() throws Exception {
        statements.givenTheApplicationIsReady();

        statements.whenHealthIsRequested();

        statements.assertAnsweredUpWith200();
    }

    @Test
    void shouldAnswer503DownWhenTheApplicationIsNotReady() throws Exception {
        statements.givenTheApplicationIsNotReady();

        statements.whenHealthIsRequested();

        statements.assertAnsweredDownWith503();
    }
}
