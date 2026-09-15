package com.uwords.adapter.rest.dto.auth;

import com.uwords.usecase.service.auth.StartedChallenge;
import java.util.UUID;

public record ChallengeStartResponseDto(UUID challengeId, String challengeType, String expiresAt) {

    public static ChallengeStartResponseDto from(StartedChallenge started) {
        return new ChallengeStartResponseDto(
                started.challengeId(),
                started.challengeType().value(),
                started.expiresAt().toString());
    }
}
