package com.uwords.adapter.rest.dto.auth;

import com.uwords.usecase.service.auth.RotatedSessionTokens;

public record SessionRefreshResponseDto(RotatedSessionDto session) {

    public static SessionRefreshResponseDto from(RotatedSessionTokens rotated) {
        return new SessionRefreshResponseDto(
                new RotatedSessionDto(rotated.sessionId(), rotated.refreshToken(), rotated.accessToken()));
    }
}
