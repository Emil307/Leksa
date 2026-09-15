package com.uwords.adapter.rest.dto.auth;

import com.uwords.usecase.service.auth.VerifiedSession;

public record ChallengeVerifyResponseDto(VerifiedUserDto user, IssuedSessionDto session) {

    public static ChallengeVerifyResponseDto from(VerifiedSession verified) {
        return new ChallengeVerifyResponseDto(
                new VerifiedUserDto(verified.userId()),
                new IssuedSessionDto(verified.sessionId(), verified.refreshToken(), verified.accessToken()));
    }
}
