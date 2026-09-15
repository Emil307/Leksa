package com.uwords.usecase.testing.statements;

import com.uwords.domain.auth.user.Gender;
import com.uwords.domain.auth.user.User;
import java.time.Instant;
import java.time.LocalDate;
import java.util.UUID;

public final class AuthData {

    public static final Instant NOW = Instant.parse("2026-08-16T12:00:00Z");
    public static final Instant TOKEN_EXPIRES_AT = NOW.plusSeconds(15 * 60);
    public static final Instant SESSION_EXPIRES_AT = NOW.plusSeconds(60 * 60);
    public static final Instant SHORT_SESSION_EXPIRES_AT = NOW.plusSeconds(5 * 60);

    public static final UUID USER_ID = UUID.fromString("11111111-1111-4111-8111-111111111111");
    public static final UUID OTHER_USER_ID = UUID.fromString("22222222-2222-4222-8222-222222222222");
    public static final UUID SESSION_ID = UUID.fromString("33333333-3333-4333-8333-333333333333");
    public static final UUID SHORT_SESSION_ID = UUID.fromString("44444444-4444-4444-8444-444444444444");
    public static final UUID FOREIGN_SESSION_ID = UUID.fromString("55555555-5555-4555-8555-555555555555");
    public static final UUID UNKNOWN_SESSION_ID = UUID.fromString("66666666-6666-4666-8666-666666666666");
    public static final UUID LEGACY_SESSION_ID = UUID.fromString("77777777-7777-4777-8777-777777777777");
    public static final UUID TOKEN_ID = UUID.fromString("88888888-8888-4888-8888-888888888888");
    public static final UUID AVATAR_ID = UUID.fromString("99999999-9999-4999-8999-999999999999");

    public static final String VALID_TOKEN = "valid.access.token";
    public static final String SHORT_SESSION_TOKEN = "short.session.token";
    public static final String FOREIGN_SESSION_TOKEN = "foreign.session.token";
    public static final String UNKNOWN_SESSION_TOKEN = "unknown.session.token";
    public static final String LEGACY_SESSION_TOKEN = "legacy.session.token";
    public static final String INCOMPLETE_TOKEN = "incomplete.claims.token";
    public static final String FORGED_TOKEN = "forged.signature.token";

    public static final String OTHER_SCHEME = "Basic";

    public static final User STORED_USER = new User(
            USER_ID,
            "Мария",
            "Иванова",
            "maria@example.com",
            false,
            Instant.parse("2025-03-01T09:30:00Z"),
            Instant.parse("2026-08-15T18:45:00Z"),
            AVATAR_ID,
            LocalDate.of(1993, 4, 17),
            Gender.FEMALE,
            "Казань",
            "+79990000001");

    private AuthData() {
    }
}
