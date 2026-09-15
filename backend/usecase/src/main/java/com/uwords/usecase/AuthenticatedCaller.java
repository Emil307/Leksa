package com.uwords.usecase;

import java.util.UUID;

public record AuthenticatedCaller(UUID userId, UUID sessionId) {
}
