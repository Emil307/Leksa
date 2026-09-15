package com.uwords.adapter.storage.testing.statements;

import static org.assertj.core.api.Assertions.assertThat;

import com.uwords.adapter.storage.repository.SessionIssuanceRepository;
import com.uwords.adapter.storage.repository.SessionRepository;
import com.uwords.adapter.storage.testing.SessionRows;
import com.uwords.adapter.storage.testing.SessionRows.StoredSession;
import com.uwords.domain.auth.session.RefreshToken;
import com.uwords.domain.auth.session.Session;
import com.uwords.domain.auth.user.AuthProvider;
import com.uwords.domain.auth.user.ProviderAccount;
import com.uwords.usecase.port.auth.session.SessionIssuanceRequest;
import java.time.Instant;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import javax.sql.DataSource;

public class SessionRepositoryStatements {

    private static final ProviderAccount ACCOUNT =
            new ProviderAccount(AuthProvider.EMAIL, "renewing-learner@uwords.app");
    private static final UUID USER_ID = UUID.fromString("8e2d4c6a-1b3f-4d5e-9a7c-2b4d6e8f0a1c");
    private static final UUID SESSION_ID = UUID.fromString("c1a2b3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d");
    private static final RefreshToken STORED_TOKEN = new RefreshToken("stored-refresh-token-5-2-1");
    private static final RefreshToken NEW_TOKEN = new RefreshToken("rotated-refresh-token-5-2-1");
    private static final RefreshToken REPLAYED_NEW_TOKEN = new RefreshToken("replayed-refresh-token-5-2-1");
    private static final RefreshToken UNKNOWN_TOKEN = new RefreshToken("unknown-refresh-token-5-2-1");
    private static final Instant CREATED_AT = Instant.parse("2026-09-01T10:00:00Z");
    private static final Instant NOW = Instant.parse("2026-09-14T12:00:00Z");
    private static final Instant LATER = Instant.parse("2026-09-14T12:05:00Z");
    private static final Instant EXPIRES_AT = Instant.parse("2027-09-14T12:00:00Z");
    private static final Instant NEW_EXPIRES_AT = Instant.parse("2027-09-15T12:00:00Z");
    private static final Instant REPLAYED_EXPIRES_AT = Instant.parse("2027-09-15T12:05:00Z");
    private static final long SINGLE_ROW = 1L;

    private final DataSource dataSource;
    private final SessionIssuanceRepository issuance;
    private final SessionRepository repository;
    private Optional<Session> found = Optional.empty();
    private boolean rotated;

    public SessionRepositoryStatements(
            DataSource dataSource, SessionIssuanceRepository issuance, SessionRepository repository) {
        this.dataSource = dataSource;
        this.issuance = issuance;
        this.repository = repository;
    }

    public void givenLiveSession() {
        issueSessionExpiringAt(EXPIRES_AT);
    }

    public void givenSessionExpiringExactlyNow() {
        issueSessionExpiringAt(NOW);
    }

    public void givenSessionAlreadyRotatedOnce() {
        issueSessionExpiringAt(EXPIRES_AT);
        rotateStoredToken();
    }

    public void findByStoredRefreshToken() {
        found = repository.findActiveByRefreshToken(STORED_TOKEN, NOW);
    }

    public void findByUnknownRefreshToken() {
        found = repository.findActiveByRefreshToken(UNKNOWN_TOKEN, NOW);
    }

    public void rotateWithTheStoredRefreshToken() {
        rotated = rotateStoredToken();
    }

    public void replayTheConsumedRefreshToken() {
        rotated = repository.rotateRefreshToken(
                SESSION_ID, STORED_TOKEN, REPLAYED_NEW_TOKEN, REPLAYED_EXPIRES_AT, LATER);
    }

    public void assertFoundTheLiveSession() {
        assertThat(found).contains(new Session(SESSION_ID, USER_ID, STORED_TOKEN, CREATED_AT, EXPIRES_AT));
    }

    public void assertNoSessionFound() {
        assertThat(found).isEmpty();
    }

    public void assertRotatedTheSessionInPlace() {
        assertThat(rotated).isTrue();
        assertSingleStoredRow(rotatedRow());
    }

    public void assertRefusedAndLeftTheRotatedSessionUntouched() {
        assertThat(rotated).isFalse();
        assertSingleStoredRow(rotatedRow());
    }

    public void assertRefusedAndLeftTheExpiredSessionUntouched() {
        assertThat(rotated).isFalse();
        assertSingleStoredRow(expiredRow());
    }

    private void assertSingleStoredRow(StoredSession expected) {
        assertThat(SessionRows.sessionRows(dataSource, SESSION_ID)).isEqualTo(List.of(expected));
        assertThat(SessionRows.countSessions(dataSource)).isEqualTo(SINGLE_ROW);
    }

    private StoredSession expiredRow() {
        return new StoredSession(SESSION_ID, USER_ID, STORED_TOKEN.value(), NOW, CREATED_AT, CREATED_AT);
    }

    private StoredSession rotatedRow() {
        return new StoredSession(SESSION_ID, USER_ID, NEW_TOKEN.value(), NEW_EXPIRES_AT, CREATED_AT, NOW);
    }

    private boolean rotateStoredToken() {
        return repository.rotateRefreshToken(SESSION_ID, STORED_TOKEN, NEW_TOKEN, NEW_EXPIRES_AT, NOW);
    }

    private void issueSessionExpiringAt(Instant expiresAt) {
        issuance.issueSession(new SessionIssuanceRequest(
                ACCOUNT, USER_ID, SESSION_ID, STORED_TOKEN, CREATED_AT, expiresAt));
    }
}
