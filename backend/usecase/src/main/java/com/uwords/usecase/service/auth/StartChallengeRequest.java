package com.uwords.usecase.service.auth;

import com.uwords.domain.auth.challenge.ChallengeType;

public record StartChallengeRequest(String credential, String challengeType) {

    public ChallengeType parsedType() {
        return ChallengeType.from(challengeType);
    }
}
