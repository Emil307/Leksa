package com.uwords.usecase.service.auth;

public record VerifyChallengeRequest(Object challengeId, Object code) {

    @Override
    public String toString() {
        return "VerifyChallengeRequest(challengeId=" + challengeId + ", code=<redacted>)";
    }
}
