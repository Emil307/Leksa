package com.uwords.adapter.storage;

import com.uwords.usecase.port.system.HealthCheckPort;
import java.sql.Connection;
import java.sql.SQLException;
import java.sql.Statement;
import javax.sql.DataSource;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Component;

@Component
public class DatabaseHealthCheck implements HealthCheckPort {

    private static final Logger log = LoggerFactory.getLogger(DatabaseHealthCheck.class);
    private static final String PING_QUERY = "SELECT 1";

    private final DataSource dataSource;

    public DatabaseHealthCheck(DataSource dataSource) {
        this.dataSource = dataSource;
    }

    @Override
    public boolean ping() {
        try (Connection connection = dataSource.getConnection();
                Statement statement = connection.createStatement()) {
            statement.execute(PING_QUERY);
            return true;
        } catch (SQLException | RuntimeException error) {
            log.warn("Database health check failed", error);
            return false;
        }
    }
}
