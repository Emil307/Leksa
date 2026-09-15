package com.uwords.adapter.storage;

import com.uwords.adapter.storage.testing.statements.AuthUsersMigrationStatements;
import javax.sql.DataSource;
import liquibase.integration.spring.SpringLiquibase;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.context.DynamicPropertyRegistry;
import org.springframework.test.context.DynamicPropertySource;
import org.testcontainers.containers.PostgreSQLContainer;

@SpringBootTest
@ActiveProfiles("migration")
class AuthUsersMigrationTest {

    private static final String POSTGRES_IMAGE = "postgres:17-alpine";
    private static final PostgreSQLContainer<?> POSTGRES = new PostgreSQLContainer<>(POSTGRES_IMAGE);

    static {
        POSTGRES.start();
    }

    @Autowired
    private DataSource dataSource;

    @Autowired
    private SpringLiquibase liquibase;

    private AuthUsersMigrationStatements statements;

    @DynamicPropertySource
    static void databaseProperties(DynamicPropertyRegistry registry) {
        registry.add("db.host", POSTGRES::getHost);
        registry.add("db.port", () -> POSTGRES.getMappedPort(PostgreSQLContainer.POSTGRESQL_PORT));
        registry.add("db.name", POSTGRES::getDatabaseName);
        registry.add("db.user", POSTGRES::getUsername);
        registry.add("db.password", POSTGRES::getPassword);
    }

    @BeforeEach
    void createStatements() {
        statements = new AuthUsersMigrationStatements(dataSource, liquibase);
    }

    @Test
    void shouldReachTheSameStateWhenReapplied() throws Exception {
        statements.reapplyAuthUsersFromThePreviousRevision();

        statements.assertAuthUsersSchemaIsComplete();
    }

    @Test
    void shouldCompleteTheTableWhenOnlyTheEnumExists() throws Exception {
        statements.reapplyAuthUsersAfterTheUsersTableWasDropped();

        statements.assertAuthUsersSchemaIsComplete();
    }
}
