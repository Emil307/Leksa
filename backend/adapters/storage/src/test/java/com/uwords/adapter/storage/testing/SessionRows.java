package com.uwords.adapter.storage.testing;

import static com.uwords.adapter.storage.testing.ResultSetColumns.instantOf;

import java.sql.ResultSet;
import java.sql.SQLException;
import java.time.Instant;
import java.util.List;
import java.util.UUID;
import javax.sql.DataSource;
import org.springframework.jdbc.core.JdbcTemplate;

public final class SessionRows {

    private static final String SELECT_SESSION =
            "SELECT id, user_id, refresh_token, expires_at, created_at, updated_at FROM auth.t_sessions "
                    + "WHERE id = ?";
    private static final String COUNT_SESSIONS = "SELECT count(*) FROM auth.t_sessions";

    private SessionRows() {
    }

    public static List<StoredSession> sessionRows(DataSource dataSource, UUID sessionId) {
        return new JdbcTemplate(dataSource).query(SELECT_SESSION, SessionRows::storedSession, sessionId);
    }

    public static long countSessions(DataSource dataSource) {
        return new JdbcTemplate(dataSource).queryForObject(COUNT_SESSIONS, Long.class);
    }

    private static StoredSession storedSession(ResultSet row, int index) throws SQLException {
        return new StoredSession(
                row.getObject("id", UUID.class),
                row.getObject("user_id", UUID.class),
                row.getString("refresh_token"),
                instantOf(row, "expires_at"),
                instantOf(row, "created_at"),
                instantOf(row, "updated_at"));
    }

    public record StoredSession(
            UUID id, UUID userId, String refreshToken, Instant expiresAt, Instant createdAt, Instant updatedAt) {
    }
}
