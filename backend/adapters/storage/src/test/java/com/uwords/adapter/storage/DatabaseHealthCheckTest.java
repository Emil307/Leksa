package com.uwords.adapter.storage;

import com.uwords.adapter.storage.testing.statements.HealthStatements;
import java.sql.SQLException;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class DatabaseHealthCheckTest extends StorageTest {

    private HealthStatements statements;

    @BeforeEach
    void createStatements() {
        statements = new HealthStatements(dataSource);
    }

    @Test
    void shouldReportAvailableWhenQuerySucceeds() {
        statements.pingTheReachableDatabase();

        statements.assertDatabaseIsAvailable();
    }

    @Test
    void shouldReportUnavailableWhenQueryFails() throws SQLException {
        statements.pingTheUnreachableDatabase();

        statements.assertDatabaseIsUnavailable();
    }
}
