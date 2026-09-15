package com.uwords.adapter.storage.testing;

import com.uwords.adapter.storage.testing.SessionIssuanceRows.AccountRow;
import com.uwords.adapter.storage.testing.SessionIssuanceRows.SessionRow;
import com.uwords.domain.auth.session.RefreshToken;
import com.uwords.domain.auth.user.AuthProvider;
import com.uwords.domain.auth.user.ProviderAccount;
import java.time.Instant;
import java.util.List;
import java.util.UUID;

public final class SessionIssuanceData {

    public static final String EMAIL = "existing-learner@uwords.app";
    public static final String EMPTY_NAME = "";
    public static final Instant CREATED_AT = Instant.parse("2026-09-03T10:00:00Z");
    public static final Instant EXPIRES_AT = Instant.parse("2027-09-03T10:00:00Z");
    public static final ProviderAccount ACCOUNT = new ProviderAccount(AuthProvider.EMAIL, EMAIL);
    public static final UUID FIRST_SESSION_ID = UUID.fromString("3f5e1a2b-7c8d-4e9f-8a1b-2c3d4e5f6a7b");
    public static final UUID SECOND_SESSION_ID = UUID.fromString("4a6b2c3d-8e9f-4a1b-9c2d-3e4f5a6b7c8d");
    public static final RefreshToken FIRST_REFRESH_TOKEN = new RefreshToken("first-refresh-token-4-1");
    public static final RefreshToken SECOND_REFRESH_TOKEN = new RefreshToken("second-refresh-token-4-1");

    public static final UUID EXISTING_USER_ID = UUID.fromString("2c1f7f7a-6d2f-4d6c-9f0e-0f3a1b2c3d4e");
    public static final UUID CANDIDATE_USER_ID = UUID.fromString("9b8a7c6d-5e4f-4a3b-8c2d-1e0f9a8b7c6d");
    public static final UUID MIXED_CASE_USER_ID = UUID.fromString("5d4c3b2a-1f0e-4d9c-8b7a-6f5e4d3c2b1a");
    public static final UUID WHITESPACE_USER_ID = UUID.fromString("7a6b5c4d-3e2f-4a1b-9c8d-7e6f5a4b3c2d");
    public static final String STORED_MIXED_CASE_EMAIL = "Existing-Learner@Uwords.App";
    public static final String STORED_WHITESPACE_EMAIL = "  existing-learner@uwords.app  ";

    public static final List<UUID> ALL_USER_IDS =
            List.of(EXISTING_USER_ID, CANDIDATE_USER_ID, MIXED_CASE_USER_ID, WHITESPACE_USER_ID);

    private SessionIssuanceData() {
    }

    public static List<AccountRow> accountRowsOf(UUID userId) {
        return List.of(new AccountRow(userId, AuthProvider.EMAIL.value(), EMAIL, CREATED_AT));
    }

    public static SessionRow firstSessionRowOf(UUID userId) {
        return new SessionRow(FIRST_SESSION_ID, userId, FIRST_REFRESH_TOKEN.value(), EXPIRES_AT, CREATED_AT);
    }

    public static SessionRow secondSessionRowOf(UUID userId) {
        return new SessionRow(SECOND_SESSION_ID, userId, SECOND_REFRESH_TOKEN.value(), EXPIRES_AT, CREATED_AT);
    }
}
