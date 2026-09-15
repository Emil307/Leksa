package com.uwords.adapter.storage.testing.statements;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.InstanceOfAssertFactories.STRING;

import java.util.List;
import java.util.Set;
import javax.sql.DataSource;
import liquibase.integration.spring.SpringLiquibase;
import org.springframework.jdbc.core.JdbcTemplate;

public class AuthUsersMigrationStatements {

    private static final List<String> GENDER_LABELS = List.of("male", "female");
    private static final Set<String> USERS_COLUMN_NAMES = Set.of(
            "id", "name", "surname", "email", "is_superuser", "created_at",
            "updated_at", "avatar_id", "birthday", "gender", "city", "phone");
    private static final String GENDER_LABEL_QUERY = """
            SELECT e.enumlabel FROM pg_enum e
            JOIN pg_type t ON t.oid = e.enumtypid
            JOIN pg_namespace n ON n.oid = t.typnamespace
            WHERE t.typname = 'user_gender' AND n.nspname = 'auth'
            ORDER BY e.enumsortorder
            """;
    private static final String USERS_TABLE_QUERY = """
            SELECT count(*) FROM information_schema.tables
            WHERE table_schema = 'auth' AND table_name = 't_users'
            """;
    private static final String USERS_COLUMN_QUERY = """
            SELECT column_name FROM information_schema.columns
            WHERE table_schema = 'auth' AND table_name = 't_users'
            """;
    private static final String NORMALIZED_INDEX_QUERY = """
            SELECT indexdef FROM pg_indexes
            WHERE schemaname = 'auth' AND indexname = 'uq_t_users_email_normalized'
            """;
    private static final String FORGET_AUTH_USERS_CHANGESETS =
            "DELETE FROM databasechangelog WHERE id LIKE '0002-%'";
    private static final String DROP_USERS_TABLE = "DROP TABLE IF EXISTS auth.t_users CASCADE";

    private final JdbcTemplate jdbcTemplate;
    private final SpringLiquibase liquibase;

    public AuthUsersMigrationStatements(DataSource dataSource, SpringLiquibase liquibase) {
        this.jdbcTemplate = new JdbcTemplate(dataSource);
        this.liquibase = liquibase;
    }

    public void reapplyAuthUsersFromThePreviousRevision() throws Exception {
        jdbcTemplate.update(FORGET_AUTH_USERS_CHANGESETS);
        liquibase.afterPropertiesSet();
    }

    public void reapplyAuthUsersAfterTheUsersTableWasDropped() throws Exception {
        jdbcTemplate.execute(DROP_USERS_TABLE);
        reapplyAuthUsersFromThePreviousRevision();
    }

    public void assertAuthUsersSchemaIsComplete() {
        assertThat(jdbcTemplate.queryForList(GENDER_LABEL_QUERY, String.class))
                .isEqualTo(GENDER_LABELS);
        assertThat(jdbcTemplate.queryForObject(USERS_TABLE_QUERY, Integer.class)).isEqualTo(1);
        assertThat(Set.copyOf(jdbcTemplate.queryForList(USERS_COLUMN_QUERY, String.class)))
                .isEqualTo(USERS_COLUMN_NAMES);
        assertThat(jdbcTemplate.queryForList(NORMALIZED_INDEX_QUERY, String.class))
                .singleElement(STRING)
                .contains("UNIQUE INDEX")
                .contains("lower(btrim((email)::text))");
    }
}
