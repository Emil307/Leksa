package com.uwords.usecase.testing.fakes;

import com.uwords.domain.auth.failure.AuthFailureReason;
import com.uwords.domain.auth.failure.Unauthorized;
import com.uwords.domain.auth.session.ActiveSession;
import com.uwords.domain.common.UnavailableException;
import com.uwords.usecase.port.auth.session.ActiveSessionRepositoryPort;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.UUID;

public class FakeActiveSessionRepository implements ActiveSessionRepositoryPort {

    public final Map<UUID, ActiveSession> sessions = new HashMap<>();
    public final Set<UUID> legacyIds = new HashSet<>();
    public boolean unavailable;

    @Override
    public Optional<ActiveSession> findById(UUID sessionId) {
        if (unavailable) {
            throw new UnavailableException("session storage is unreachable");
        }
        if (legacyIds.contains(sessionId)) {
            throw Unauthorized.of(AuthFailureReason.LEGACY_SESSION);
        }
        return Optional.ofNullable(sessions.get(sessionId));
    }
}
