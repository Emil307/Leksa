package com.uwords.adapter.storage.testing;

import static com.uwords.adapter.storage.testing.ResultSetColumns.instantOf;

import java.sql.ResultSet;
import java.sql.SQLException;
import java.time.Instant;
import java.util.List;
import java.util.UUID;
import java.util.stream.Collectors;
import javax.sql.DataSource;
import org.springframework.jdbc.core.JdbcTemplate;

public final class SessionIssuanceRows {

    private static final String INSERT_USER = "INSERT INTO auth.t_users (id, name, email) VALUES (?, ?, ?)";
    private static final String SELECT_USER_IDS =
            "SELECT id FROM auth.t_users WHERE id IN (%s) ORDER BY id";
    private static final String SELECT_IDENTITIES =
            "SELECT id, name, email FROM auth.t_users WHERE id IN (%s) ORDER BY id";
    private static final String SELECT_ACCOUNTS =
            "SELECT user_id, provider, provider_id, created_at FROM auth.t_auth "
                    + "WHERE user_id IN (%s) ORDER BY provider_id";
    private static final String SELECT_SESSIONS =
            "SELECT id, user_id, refresh_token, expires_at, created_at FROM auth.t_sessions "
                    + "WHERE user_id IN (%s) ORDER BY refresh_token";
    private static final String PLACEHOLDER = "?";
    private static final String PLACEHOLDER_SEPARATOR = ", ";

    private SessionIssuanceRows() {
    }

    public static void givenStoredUser(DataSource dataSource, UUID userId, String email) {
        new JdbcTemplate(dataSource).update(INSERT_USER, userId, SessionIssuanceData.EMPTY_NAME, email);
    }

    public static List<UUID> userIds(DataSource dataSource, List<UUID> candidates) {
        return new JdbcTemplate(dataSource).query(
                expand(SELECT_USER_IDS, candidates), SessionIssuanceRows::userId, identifiers(candidates));
    }

    public static List<IdentityRow> identityRows(DataSource dataSource, List<UUID> candidates) {
        return new JdbcTemplate(dataSource).query(
                expand(SELECT_IDENTITIES, candidates), SessionIssuanceRows::identityRow, identifiers(candidates));
    }

    public static List<AccountRow> accountRows(DataSource dataSource, List<UUID> candidates) {
        return new JdbcTemplate(dataSource).query(
                expand(SELECT_ACCOUNTS, candidates), SessionIssuanceRows::accountRow, identifiers(candidates));
    }

    public static List<SessionRow> sessionRows(DataSource dataSource, List<UUID> candidates) {
        return new JdbcTemplate(dataSource).query(
                expand(SELECT_SESSIONS, candidates), SessionIssuanceRows::sessionRow, identifiers(candidates));
    }

    private static String expand(String template, List<UUID> candidates) {
        return template.formatted(candidates.stream()
                .map(candidate -> PLACEHOLDER)
                .collect(Collectors.joining(PLACEHOLDER_SEPARATOR)));
    }

    private static Object[] identifiers(List<UUID> candidates) {
        return candidates.toArray(Object[]::new);
    }

    private static UUID userId(ResultSet row, int index) throws SQLException {
        return row.getObject("id", UUID.class);
    }

    private static IdentityRow identityRow(ResultSet row, int index) throws SQLException {
        return new IdentityRow(row.getObject("id", UUID.class), row.getString("name"), row.getString("email"));
    }

    private static AccountRow accountRow(ResultSet row, int index) throws SQLException {
        return new AccountRow(
                row.getObject("user_id", UUID.class),
                row.getString("provider"),
                row.getString("provider_id"),
                instantOf(row, "created_at"));
    }

    private static SessionRow sessionRow(ResultSet row, int index) throws SQLException {
        return new SessionRow(
                row.getObject("id", UUID.class),
                row.getObject("user_id", UUID.class),
                row.getString("refresh_token"),
                instantOf(row, "expires_at"),
                instantOf(row, "created_at"));
    }

    public record IdentityRow(UUID id, String name, String email) {
    }

    public record AccountRow(UUID userId, String provider, String providerId, Instant createdAt) {
    }

    public record SessionRow(UUID id, UUID userId, String refreshToken, Instant expiresAt, Instant createdAt) {
    }
}
