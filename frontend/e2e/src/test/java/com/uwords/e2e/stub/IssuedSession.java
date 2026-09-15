package com.uwords.e2e.stub;

public record IssuedSession(String userId, String sessionId, String accessToken, String refreshToken) {
}
