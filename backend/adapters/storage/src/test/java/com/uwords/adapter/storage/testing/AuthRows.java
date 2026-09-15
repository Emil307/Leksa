package com.uwords.adapter.storage.testing;

import com.uwords.domain.auth.user.Gender;
import java.sql.Timestamp;
import java.time.Instant;
import java.util.UUID;
import javax.sql.DataSource;
import org.springframework.jdbc.core.JdbcTemplate;

public final class AuthRows {

    private static final String INSERT_FULL_USER =
            "INSERT INTO auth.t_users (id, name, surname, email, is_superuser, created_at, updated_at, "
                    + "avatar_id, birthday, gender, city, phone) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)";
    private static final String INSERT_NAMED_USER = "INSERT INTO auth.t_users (id, name) VALUES (?, ?)";
    private static final String INSERT_USER_WITH_RAW_GENDER =
            "INSERT INTO auth.t_users (id, name, gender) VALUES (?, ?, ?)";
    private static final String INSERT_USER_WITH_EMAIL =
            "INSERT INTO auth.t_users (id, name, email) VALUES (?, ?, ?)";
    private static final String INSERT_SESSION =
            "INSERT INTO auth.t_sessions (id, user_id, refresh_token, expires_at, created_at, updated_at) "
                    + "VALUES (?, ?, ?, ?, ?, ?)";

    private AuthRows() {
    }

    public static void givenStoredFullUser(DataSource dataSource, UUID userId) {
        new JdbcTemplate(dataSource).update(
                INSERT_FULL_USER,
                userId,
                AuthData.USER_NAME,
                AuthData.USER_SURNAME,
                AuthData.emailOf(userId),
                true,
                timestampOf(AuthData.USER_CREATED_AT),
                timestampOf(AuthData.USER_UPDATED_AT),
                AuthData.AVATAR_ID,
                java.sql.Date.valueOf(AuthData.USER_BIRTHDAY),
                Gender.MALE.value(),
                AuthData.USER_CITY,
                AuthData.USER_PHONE);
    }

    public static void givenStoredMinimalUser(DataSource dataSource, UUID userId) {
        new JdbcTemplate(dataSource).update(INSERT_NAMED_USER, userId, AuthData.USER_NAME);
    }

    public static void givenStoredUserWithOutOfDomainGender(DataSource dataSource, UUID userId) {
        new JdbcTemplate(dataSource).update(
                INSERT_USER_WITH_RAW_GENDER, userId, AuthData.USER_NAME, AuthSchema.OUT_OF_DOMAIN_GENDER);
    }

    public static void givenStoredUserWithEmail(DataSource dataSource, UUID userId, String email) {
        new JdbcTemplate(dataSource).update(INSERT_USER_WITH_EMAIL, userId, "", email);
    }

    public static void givenLiveSession(DataSource dataSource, UUID sessionId, UUID userId) {
        insertSession(dataSource, sessionId, userId, timestampOf(AuthData.SESSION_EXPIRES_AT));
    }

    public static void givenLegacySession(DataSource dataSource, UUID sessionId, UUID userId) {
        insertSession(dataSource, sessionId, userId, null);
    }

    private static void insertSession(DataSource dataSource, UUID sessionId, UUID userId, Timestamp expiresAt) {
        new JdbcTemplate(dataSource).update(
                INSERT_SESSION,
                sessionId,
                userId,
                AuthData.refreshTokenOf(sessionId),
                expiresAt,
                timestampOf(AuthData.USER_CREATED_AT),
                timestampOf(AuthData.USER_UPDATED_AT));
    }

    private static Timestamp timestampOf(Instant moment) {
        return Timestamp.from(moment);
    }
}
