package com.uwords.usecase.port.auth.session;

import com.uwords.domain.auth.session.RefreshToken;
import com.uwords.domain.auth.user.ProviderAccount;
import java.time.Instant;
import java.util.UUID;

public record SessionIssuanceRequest(
        ProviderAccount account,
        UUID candidateUserId,
        UUID sessionId,
        RefreshToken refreshToken,
        Instant createdAt,
        Instant expiresAt) {
}
