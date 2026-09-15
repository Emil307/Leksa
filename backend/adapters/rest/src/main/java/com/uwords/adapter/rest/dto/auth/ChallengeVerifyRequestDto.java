package com.uwords.adapter.rest.dto.auth;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.uwords.usecase.service.auth.VerifyChallengeRequest;

@JsonIgnoreProperties(ignoreUnknown = true)
public record ChallengeVerifyRequestDto(Object challengeId, Object code) {

    public VerifyChallengeRequest toUsecaseRequest() {
        return new VerifyChallengeRequest(challengeId, code);
    }

    @Override
    public String toString() {
        return "ChallengeVerifyRequestDto(challengeId=" + challengeId + ", code=<redacted>)";
    }
}
