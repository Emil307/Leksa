package com.uwords.domain.auth.challenge;

import com.uwords.domain.common.ValidationException;

public enum ChallengeType {
    EMAIL_CODE("EMAIL_CODE");

    public static final String UNSUPPORTED_CHALLENGE_TYPE_MESSAGE = "Challenge type is not supported";
    public static final String CHALLENGE_TYPE_REQUIRED_MESSAGE = "Challenge type is required";

    private final String value;

    ChallengeType(String value) {
        this.value = value;
    }

    public String value() {
        return value;
    }

    public static ChallengeType from(String raw) {
        if (raw == null || raw.strip().isEmpty()) {
            throw new ValidationException(CHALLENGE_TYPE_REQUIRED_MESSAGE);
        }
        String candidate = raw.strip();
        for (ChallengeType challengeType : values()) {
            if (challengeType.value.equals(candidate)) {
                return challengeType;
            }
        }
        throw new ValidationException(UNSUPPORTED_CHALLENGE_TYPE_MESSAGE);
    }
}
