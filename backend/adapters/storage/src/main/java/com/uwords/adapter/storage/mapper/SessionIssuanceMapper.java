package com.uwords.adapter.storage.mapper;

import com.uwords.adapter.storage.entity.AuthAccountEntity;
import com.uwords.adapter.storage.entity.SessionEntity;
import com.uwords.adapter.storage.entity.UserEntity;
import com.uwords.usecase.port.auth.session.SessionIssuanceRequest;
import java.util.UUID;

public final class SessionIssuanceMapper {

    public static final String EMPTY_NAME = "";

    private SessionIssuanceMapper() {
    }

    public static UserEntity toUserEntity(SessionIssuanceRequest request) {
        UserEntity entity = new UserEntity();
        entity.setId(request.candidateUserId());
        entity.setName(EMPTY_NAME);
        entity.setEmail(request.account().providerId());
        entity.setCreatedAt(request.createdAt());
        entity.setUpdatedAt(request.createdAt());
        return entity;
    }

    public static AuthAccountEntity toAccountEntity(SessionIssuanceRequest request, UUID userId) {
        AuthAccountEntity entity = new AuthAccountEntity();
        entity.setId(UUID.randomUUID());
        entity.setUserId(userId);
        entity.setProvider(request.account().provider().value());
        entity.setProviderId(request.account().providerId());
        entity.setCreatedAt(request.createdAt());
        entity.setUpdatedAt(request.createdAt());
        return entity;
    }

    public static SessionEntity toSessionEntity(SessionIssuanceRequest request, UUID userId) {
        SessionEntity entity = new SessionEntity();
        entity.setId(request.sessionId());
        entity.setUserId(userId);
        entity.setRefreshToken(request.refreshToken().value());
        entity.setExpiresAt(request.expiresAt());
        entity.setCreatedAt(request.createdAt());
        entity.setUpdatedAt(request.createdAt());
        return entity;
    }
}
