package com.uwords.usecase.service.auth;

import java.util.UUID;

public record VerifiedSession(UUID userId, UUID sessionId, String refreshToken, String accessToken) {

    @Override
    public String toString() {
        return "VerifiedSession(userId=" + userId
                + ", sessionId=" + sessionId
                + ", refreshToken=<redacted>, accessToken=<redacted>)";
    }
}
