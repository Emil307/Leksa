package com.uwords.adapter.storage.testing;

import java.util.List;
import javax.sql.DataSource;
import org.springframework.jdbc.core.JdbcTemplate;

public final class AuthSchema {

    public static final String OUT_OF_DOMAIN_GENDER = "other";

    private static final String WIDEN_GENDER_TYPE =
            "ALTER TYPE auth.user_gender ADD VALUE IF NOT EXISTS '" + OUT_OF_DOMAIN_GENDER + "'";
    private static final String DROP_EXPIRES_AT_NOT_NULL =
            "ALTER TABLE auth.t_sessions ALTER COLUMN expires_at DROP NOT NULL";
    private static final String DELETE_LEGACY_SESSIONS =
            "DELETE FROM auth.t_sessions WHERE expires_at IS NULL";
    private static final String SET_EXPIRES_AT_NOT_NULL =
            "ALTER TABLE auth.t_sessions ALTER COLUMN expires_at SET NOT NULL";
    private static final List<String> CLEAR_STATEMENTS = List.of(
            "DELETE FROM auth.t_sessions",
            "DELETE FROM auth.t_auth",
            "DELETE FROM auth.t_users",
            "DELETE FROM notifications.t_outbox");

    private AuthSchema() {
    }

    public static void widenGenderType(DataSource dataSource) {
        new JdbcTemplate(dataSource).execute(WIDEN_GENDER_TYPE);
    }

    public static void allowLegacySessionRows(DataSource dataSource) {
        new JdbcTemplate(dataSource).execute(DROP_EXPIRES_AT_NOT_NULL);
    }

    public static void forbidLegacySessionRows(DataSource dataSource) {
        JdbcTemplate jdbcTemplate = new JdbcTemplate(dataSource);
        jdbcTemplate.execute(DELETE_LEGACY_SESSIONS);
        jdbcTemplate.execute(SET_EXPIRES_AT_NOT_NULL);
    }

    public static void clearRows(DataSource dataSource) {
        JdbcTemplate jdbcTemplate = new JdbcTemplate(dataSource);
        CLEAR_STATEMENTS.forEach(jdbcTemplate::execute);
    }
}
