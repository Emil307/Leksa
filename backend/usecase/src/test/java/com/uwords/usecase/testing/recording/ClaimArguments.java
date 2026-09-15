package com.uwords.usecase.testing.recording;

import java.util.UUID;

public record ClaimArguments(UUID challengeId, int maxAttempts) {
}
