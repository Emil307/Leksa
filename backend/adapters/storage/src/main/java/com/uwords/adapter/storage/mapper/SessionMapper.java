package com.uwords.adapter.storage.mapper;

import com.uwords.adapter.storage.entity.SessionEntity;
import com.uwords.domain.auth.session.RefreshToken;
import com.uwords.domain.auth.session.Session;

public final class SessionMapper {

    private SessionMapper() {
    }

    public static Session toDomain(SessionEntity entity) {
        return new Session(
                entity.getId(),
                entity.getUserId(),
                new RefreshToken(entity.getRefreshToken()),
                entity.getCreatedAt(),
                entity.getExpiresAt());
    }
}
