package com.uwords.adapter.storage.repository;

import com.uwords.adapter.storage.entity.SessionEntity;
import com.uwords.adapter.storage.mapper.ActiveSessionMapper;
import com.uwords.domain.auth.failure.AuthFailureReason;
import com.uwords.domain.auth.failure.Unauthorized;
import com.uwords.domain.auth.session.ActiveSession;
import com.uwords.domain.common.UnavailableException;
import com.uwords.usecase.port.auth.session.ActiveSessionRepositoryPort;
import jakarta.persistence.EntityManager;
import jakarta.persistence.PersistenceException;
import java.util.Optional;
import java.util.UUID;
import org.springframework.dao.DataAccessException;
import org.springframework.stereotype.Repository;
import org.springframework.transaction.annotation.Transactional;

@Repository
public class ActiveSessionRepository extends StorageRepository implements ActiveSessionRepositoryPort {

    public static final String UNAVAILABLE_MESSAGE = "Session storage is unavailable";

    public ActiveSessionRepository(EntityManager entityManager) {
        super(entityManager);
    }

    @Override
    @Transactional
    public Optional<ActiveSession> findById(UUID sessionId) {
        return readStored(sessionId).map(ActiveSessionRepository::toActiveSession);
    }

    private Optional<SessionEntity> readStored(UUID sessionId) {
        try {
            return getOne(SessionEntity.class, sessionId);
        } catch (PersistenceException | DataAccessException error) {
            throw new UnavailableException(UNAVAILABLE_MESSAGE, null, false);
        }
    }

    private static ActiveSession toActiveSession(SessionEntity entity) {
        return ActiveSessionMapper.toDomain(entity)
                .orElseThrow(() -> Unauthorized.of(AuthFailureReason.LEGACY_SESSION));
    }
}
