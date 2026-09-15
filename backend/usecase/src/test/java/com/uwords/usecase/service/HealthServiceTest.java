package com.uwords.usecase.service;

import com.uwords.usecase.testing.fakes.FakeHealthCheck;
import com.uwords.usecase.testing.statements.HealthStatements;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class HealthServiceTest {

    private HealthStatements statements;

    @BeforeEach
    void createStatements() {
        statements = new HealthStatements(new FakeHealthCheck());
    }

    @Test
    void shouldBeReadyWhenDatabaseAnswers() {
        statements.givenDatabaseAvailable();

        statements.assertApplicationIsReady();
    }

    @Test
    void shouldNotBeReadyWhenDatabaseIsUnreachable() {
        statements.givenDatabaseUnreachable();

        statements.assertApplicationIsNotReady();
    }
}
