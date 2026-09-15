package com.uwords.usecase.service.auth;

import java.util.UUID;

public record RotatedSessionTokens(UUID sessionId, String refreshToken, String accessToken) {

    @Override
    public String toString() {
        return "RotatedSessionTokens(sessionId=" + sessionId
                + ", refreshToken=<redacted>, accessToken=<redacted>)";
    }
}
