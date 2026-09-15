package com.uwords.adapter.storage.mapper;

import com.uwords.adapter.storage.entity.SessionEntity;
import com.uwords.domain.auth.session.ActiveSession;
import java.util.Optional;

public final class ActiveSessionMapper {

    private ActiveSessionMapper() {
    }

    public static Optional<ActiveSession> toDomain(SessionEntity entity) {
        return Optional.ofNullable(entity.getExpiresAt())
                .map(expiresAt -> new ActiveSession(entity.getId(), entity.getUserId(), expiresAt));
    }
}
