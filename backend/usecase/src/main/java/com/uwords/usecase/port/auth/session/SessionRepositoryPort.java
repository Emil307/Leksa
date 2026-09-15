package com.uwords.usecase.port.auth.session;

import com.uwords.domain.auth.session.RefreshToken;
import com.uwords.domain.auth.session.Session;
import java.time.Instant;
import java.util.Optional;
import java.util.UUID;

public interface SessionRepositoryPort {

    Optional<Session> findActiveByRefreshToken(RefreshToken refreshToken, Instant now);

    boolean rotateRefreshToken(
            UUID sessionId,
            RefreshToken presentedToken,
            RefreshToken newToken,
            Instant newExpiresAt,
            Instant now);
}
