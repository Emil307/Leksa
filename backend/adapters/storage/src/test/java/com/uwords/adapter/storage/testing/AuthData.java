package com.uwords.adapter.storage.testing;

import com.uwords.domain.auth.user.Gender;
import com.uwords.domain.auth.user.User;
import java.time.Instant;
import java.time.LocalDate;
import java.util.UUID;

public final class AuthData {

    public static final UUID AVATAR_ID = UUID.fromString("6f1d5a4e-0c2b-4f3a-9d8e-1b2c3d4e5f60");
    public static final String USER_NAME = "Ольга";
    public static final String USER_SURNAME = "Ку́рчатова";
    public static final String USER_CITY = "Нижний Новгород";
    public static final String USER_PHONE = "+79001234567";
    public static final Instant USER_CREATED_AT = Instant.parse("2026-03-14T09:26:53Z");
    public static final Instant USER_UPDATED_AT = Instant.parse("2026-04-01T12:00:00Z");
    public static final LocalDate USER_BIRTHDAY = LocalDate.of(1991, 2, 3);
    public static final Instant SESSION_EXPIRES_AT = Instant.parse("2027-01-02T03:04:05Z");
    public static final boolean UNSET_IS_SUPERUSER_DEFAULT = false;

    private AuthData() {
    }

    public static String emailOf(UUID userId) {
        return userId + "@uwords.test";
    }

    public static String refreshTokenOf(UUID sessionId) {
        return "refresh-" + sessionId;
    }

    public static User expectedFullUser(UUID userId) {
        return new User(
                userId,
                USER_NAME,
                USER_SURNAME,
                emailOf(userId),
                true,
                USER_CREATED_AT,
                USER_UPDATED_AT,
                AVATAR_ID,
                USER_BIRTHDAY,
                Gender.MALE,
                USER_CITY,
                USER_PHONE);
    }

    public static User expectedMinimalUser(UUID userId) {
        return new User(
                userId,
                USER_NAME,
                null,
                null,
                UNSET_IS_SUPERUSER_DEFAULT,
                null,
                null,
                null,
                null,
                null,
                null,
                null);
    }
}
