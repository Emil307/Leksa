package com.uwords.usecase.testing.fakes;

import com.uwords.domain.auth.session.RefreshToken;
import com.uwords.domain.auth.session.Session;
import com.uwords.usecase.port.auth.session.IssuedSessionRecord;
import com.uwords.usecase.port.auth.session.SessionIssuanceRequest;
import com.uwords.usecase.port.auth.session.SessionRepositoryPort;
import com.uwords.usecase.testing.recording.CallJournal;
import java.time.Instant;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;

public class FakeSessionRepository extends FakeSessionIssuance implements SessionRepositoryPort {

    public static final String FIND_ACTIVE_BY_REFRESH_TOKEN = "find_active_by_refresh_token";
    public static final String ROTATE_REFRESH_TOKEN = "rotate_refresh_token";

    public record Rotation(
            UUID sessionId,
            RefreshToken presentedToken,
            RefreshToken newToken,
            Instant newExpiresAt,
            Instant now) {
    }

    public final Map<UUID, Session> rows = new LinkedHashMap<>();

    private final CallJournal journal;

    public FakeSessionRepository(CallJournal journal) {
        super(journal);
        this.journal = journal;
    }

    @Override
    public IssuedSessionRecord issueSession(SessionIssuanceRequest request) {
        IssuedSessionRecord record = super.issueSession(request);
        rows.put(request.sessionId(), storedSession(request, record.userId()));
        return record;
    }

    @Override
    public Optional<Session> findActiveByRefreshToken(RefreshToken refreshToken, Instant now) {
        journal.record(FIND_ACTIVE_BY_REFRESH_TOKEN, refreshToken);
        return rows.values().stream()
                .filter(session -> isActiveFor(session, refreshToken, now))
                .findFirst();
    }

    @Override
    public boolean rotateRefreshToken(
            UUID sessionId,
            RefreshToken presentedToken,
            RefreshToken newToken,
            Instant newExpiresAt,
            Instant now) {
        journal.record(ROTATE_REFRESH_TOKEN,
                new Rotation(sessionId, presentedToken, newToken, newExpiresAt, now));
        Session current = rows.get(sessionId);
        if (current == null || !isActiveFor(current, presentedToken, now)) {
            return false;
        }
        rows.put(sessionId, current.rotatedTo(newToken, newExpiresAt));
        return true;
    }

    private static Session storedSession(SessionIssuanceRequest request, UUID userId) {
        return new Session(
                request.sessionId(),
                userId,
                request.refreshToken(),
                request.createdAt(),
                request.expiresAt());
    }

    private static boolean isActiveFor(Session session, RefreshToken presentedToken, Instant now) {
        return session.refreshToken().matches(presentedToken) && !session.isExpiredAt(now);
    }
}
