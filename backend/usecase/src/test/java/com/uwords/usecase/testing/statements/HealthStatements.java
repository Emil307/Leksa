package com.uwords.usecase.testing.statements;

import static org.assertj.core.api.Assertions.assertThat;

import com.uwords.usecase.service.HealthService;
import com.uwords.usecase.testing.fakes.FakeHealthCheck;

public class HealthStatements {

    private final FakeHealthCheck database;
    private final HealthService service;

    public HealthStatements(FakeHealthCheck database) {
        this.database = database;
        this.service = new HealthService(database);
    }

    public void givenDatabaseAvailable() {
        database.reachable = true;
    }

    public void givenDatabaseUnreachable() {
        database.reachable = false;
    }

    public void assertApplicationIsReady() {
        assertThat(service.isReady()).isTrue();
    }

    public void assertApplicationIsNotReady() {
        assertThat(service.isReady()).isFalse();
    }
}
