package com.uwords.adapter.rest.testing;

import com.uwords.domain.auth.user.Gender;
import com.uwords.domain.auth.user.User;
import com.uwords.usecase.AuthenticatedCaller;
import java.time.Instant;
import java.time.LocalDate;
import java.util.UUID;

public final class ProfileData {

    public static final String PROFILE_PATH = "/api/v1/profile";
    public static final String VALID_HEADER = "Bearer  eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ4In0.signature ";

    public static final UUID CALLER_USER_ID = UUID.fromString("11111111-1111-4111-8111-111111111111");
    public static final UUID CALLER_SESSION_ID = UUID.fromString("22222222-2222-4222-8222-222222222222");
    public static final UUID OTHER_USER_ID = UUID.fromString("33333333-3333-4333-8333-333333333333");
    public static final UUID AVATAR_ID = UUID.fromString("44444444-4444-4444-8444-444444444444");

    public static final AuthenticatedCaller CALLER = new AuthenticatedCaller(CALLER_USER_ID, CALLER_SESSION_ID);

    public static final User FULL_USER = new User(
            CALLER_USER_ID,
            "Иван",
            "Петров",
            "ivan.petrov@example.com",
            false,
            Instant.parse("2026-08-16T09:30:15Z"),
            Instant.parse("2026-08-17T21:05:00Z"),
            AVATAR_ID,
            LocalDate.of(1990, 2, 3),
            Gender.MALE,
            "Москва",
            "+79990000000");

    public static final User SPARSE_USER = new User(
            CALLER_USER_ID, "Ана", null, null, false, null, null, null, null, null, null, null);

    public static final String FULL_PROFILE_BODY = """
            {"id":"11111111-1111-4111-8111-111111111111",
             "name":"Иван",
             "surname":"Петров",
             "email":"ivan.petrov@example.com",
             "isSuperuser":false,
             "createdAt":"2026-08-16T09:30:15Z",
             "updatedAt":"2026-08-17T21:05:00Z",
             "avatarId":"44444444-4444-4444-8444-444444444444",
             "birthday":"1990-02-03",
             "gender":"male",
             "city":"Москва",
             "phone":"+79990000000"}""";

    public static final String SPARSE_PROFILE_BODY = """
            {"id":"11111111-1111-4111-8111-111111111111",
             "name":"Ана",
             "surname":null,
             "email":null,
             "isSuperuser":false,
             "createdAt":null,
             "updatedAt":null,
             "avatarId":null,
             "birthday":null,
             "gender":null,
             "city":null,
             "phone":null}""";

    public static final String UNAUTHORIZED_BODY = """
            {"code":"UNAUTHORIZED","message":"Unauthorized","payload":null}""";

    private ProfileData() {
    }
}
