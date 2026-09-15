package com.uwords.adapter.storage.testing.statements;

import static org.assertj.core.api.Assertions.assertThat;

import com.uwords.adapter.storage.entity.SessionEntity;
import com.uwords.adapter.storage.mapper.ActiveSessionMapper;
import com.uwords.adapter.storage.testing.AuthData;
import com.uwords.domain.auth.session.ActiveSession;
import java.util.Optional;
import java.util.UUID;

public class ActiveSessionMapperStatements {

    private final UUID sessionId = UUID.randomUUID();
    private final UUID userId = UUID.randomUUID();
    private Optional<ActiveSession> mapped = Optional.empty();

    public void mapLegacySessionRow() {
        SessionEntity entity = new SessionEntity();
        entity.setId(sessionId);
        entity.setUserId(userId);
        entity.setRefreshToken(AuthData.refreshTokenOf(sessionId));
        entity.setCreatedAt(AuthData.USER_CREATED_AT);
        entity.setUpdatedAt(AuthData.USER_UPDATED_AT);
        mapped = ActiveSessionMapper.toDomain(entity);
    }

    public void assertNoMappedSession() {
        assertThat(mapped).isEmpty();
    }
}
