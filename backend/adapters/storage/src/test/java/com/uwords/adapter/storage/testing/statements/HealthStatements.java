package com.uwords.adapter.storage.testing.statements;

import static org.assertj.core.api.Assertions.assertThat;

import com.uwords.adapter.storage.DatabaseHealthCheck;
import com.uwords.adapter.storage.testing.UnreachableStorage;
import java.sql.SQLException;
import javax.sql.DataSource;

public class HealthStatements {

    private final DataSource dataSource;
    private boolean available;

    public HealthStatements(DataSource dataSource) {
        this.dataSource = dataSource;
    }

    public void pingTheReachableDatabase() {
        available = new DatabaseHealthCheck(dataSource).ping();
    }

    public void pingTheUnreachableDatabase() throws SQLException {
        available = new DatabaseHealthCheck(UnreachableStorage.dataSource()).ping();
    }

    public void assertDatabaseIsAvailable() {
        assertThat(available).isTrue();
    }

    public void assertDatabaseIsUnavailable() {
        assertThat(available).isFalse();
    }
}
