package com.uwords.adapter.storage.repository;

import com.uwords.adapter.storage.entity.SessionEntity;
import com.uwords.adapter.storage.mapper.SessionMapper;
import com.uwords.domain.auth.session.RefreshToken;
import com.uwords.domain.auth.session.Session;
import com.uwords.usecase.port.auth.session.SessionRepositoryPort;
import jakarta.persistence.EntityManager;
import java.time.Instant;
import java.util.Optional;
import java.util.UUID;
import org.springframework.stereotype.Repository;
import org.springframework.transaction.annotation.Transactional;

@Repository
public class SessionRepository extends StorageRepository implements SessionRepositoryPort {

    private static final String ACTIVE_SESSION_QUERY =
            "select session from SessionEntity session "
                    + "where session.refreshToken = :token and session.expiresAt > :now";
    private static final String ROTATE_SESSION_UPDATE =
            "update SessionEntity session "
                    + "set session.refreshToken = :newToken, session.expiresAt = :newExpiresAt, "
                    + "session.updatedAt = :now "
                    + "where session.id = :id and session.refreshToken = :presented and session.expiresAt > :now";
    private static final String TOKEN_PARAMETER = "token";
    private static final String NOW_PARAMETER = "now";
    private static final String ID_PARAMETER = "id";
    private static final String PRESENTED_PARAMETER = "presented";
    private static final String NEW_TOKEN_PARAMETER = "newToken";
    private static final String NEW_EXPIRES_AT_PARAMETER = "newExpiresAt";
    private static final int SINGLE_ROW = 1;

    public SessionRepository(EntityManager entityManager) {
        super(entityManager);
    }

    @Override
    @Transactional
    public Optional<Session> findActiveByRefreshToken(RefreshToken refreshToken, Instant now) {
        return entityManager.createQuery(ACTIVE_SESSION_QUERY, SessionEntity.class)
                .setParameter(TOKEN_PARAMETER, refreshToken.value())
                .setParameter(NOW_PARAMETER, now)
                .setMaxResults(SINGLE_ROW)
                .getResultList()
                .stream()
                .findFirst()
                .map(SessionMapper::toDomain);
    }

    @Override
    @Transactional
    public boolean rotateRefreshToken(
            UUID sessionId,
            RefreshToken presentedToken,
            RefreshToken newToken,
            Instant newExpiresAt,
            Instant now) {
        int rotatedRows = entityManager.createQuery(ROTATE_SESSION_UPDATE)
                .setParameter(NEW_TOKEN_PARAMETER, newToken.value())
                .setParameter(NEW_EXPIRES_AT_PARAMETER, newExpiresAt)
                .setParameter(NOW_PARAMETER, now)
                .setParameter(ID_PARAMETER, sessionId)
                .setParameter(PRESENTED_PARAMETER, presentedToken.value())
                .executeUpdate();
        return rotatedRows == SINGLE_ROW;
    }
}
