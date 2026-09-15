package com.uwords.adapter.rest.dto.auth;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.uwords.usecase.service.auth.StartChallengeRequest;

@JsonIgnoreProperties(ignoreUnknown = true)
public record ChallengeStartRequestDto(String email, String challengeType) {

    public StartChallengeRequest toUsecaseRequest() {
        return new StartChallengeRequest(orEmpty(email), orEmpty(challengeType));
    }

    private static String orEmpty(String value) {
        return value == null ? "" : value;
    }
}
