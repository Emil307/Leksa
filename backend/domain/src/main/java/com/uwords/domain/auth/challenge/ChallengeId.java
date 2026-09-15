package com.uwords.domain.auth.challenge;

import com.uwords.domain.common.UuidText;
import com.uwords.domain.common.ValidationException;
import java.util.UUID;

public record ChallengeId(UUID value) {

    public static final String CHALLENGE_ID_REQUIRED_MESSAGE = "Challenge id is required";
    public static final String CHALLENGE_ID_INVALID_MESSAGE = "Challenge id is not a valid identifier";

    public static ChallengeId of(Object raw) {
        return switch (raw) {
            case String text when !text.strip().isEmpty() -> new ChallengeId(
                    UuidText.parse(text.strip())
                            .orElseThrow(() -> new ValidationException(CHALLENGE_ID_INVALID_MESSAGE)));
            case null, default -> throw new ValidationException(CHALLENGE_ID_REQUIRED_MESSAGE);
        };
    }
}
