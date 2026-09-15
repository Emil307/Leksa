package com.uwords.usecase.port.auth.session;

import java.util.UUID;

public record IssuedSessionRecord(UUID userId, UUID sessionId, boolean createdUser) {
}
