package com.uwords.usecase.service.auth;

import com.uwords.domain.auth.failure.AuthFailureReason;
import com.uwords.domain.auth.failure.Unauthorized;
import com.uwords.domain.auth.session.RefreshToken;
import com.uwords.domain.auth.session.Session;
import com.uwords.domain.auth.session.SessionPolicy;
import com.uwords.domain.common.UnauthorizedException;
import com.uwords.usecase.port.auth.session.AccessTokenIssuerPort;
import com.uwords.usecase.port.auth.session.RefreshTokenGeneratorPort;
import com.uwords.usecase.port.auth.session.SessionRepositoryPort;
import com.uwords.usecase.port.system.ClockPort;
import com.uwords.usecase.port.system.IdGeneratorPort;
import java.time.Instant;
import java.util.UUID;
import org.springframework.stereotype.Service;

@Service
public class RefreshSessionTokensService {

    private final SessionRepositoryPort sessions;
    private final RefreshTokenGeneratorPort tokens;
    private final AccessTokenIssuerPort accessTokens;
    private final ClockPort clock;
    private final IdGeneratorPort ids;
    private final SessionPolicy policy;

    public RefreshSessionTokensService(
            SessionRepositoryPort sessions,
            RefreshTokenGeneratorPort tokens,
            AccessTokenIssuerPort accessTokens,
            ClockPort clock,
            IdGeneratorPort ids,
            SessionPolicy policy) {
        this.sessions = sessions;
        this.tokens = tokens;
        this.accessTokens = accessTokens;
        this.clock = clock;
        this.ids = ids;
        this.policy = policy;
    }

    public RotatedSessionTokens refresh(RefreshSessionRequest request) {
        RefreshToken presented = RefreshToken.of(request.refreshToken());
        Instant now = clock.now();
        Session session = requireActiveSession(presented, now);
        RefreshToken newToken = RefreshToken.of(tokens.generate());
        Session rotated = session.rotate(newToken, now, policy);
        String accessToken = mintAccessToken(rotated, now);
        persistRotation(rotated, presented, now);
        return new RotatedSessionTokens(session.id(), newToken.value(), accessToken);
    }

    private String mintAccessToken(Session rotated, Instant now) {
        UUID tokenId = ids.newId();
        return accessTokens.issue(rotated.accessTokenClaims(tokenId, now, policy));
    }

    private Session requireActiveSession(RefreshToken presented, Instant now) {
        return sessions.findActiveByRefreshToken(presented, now)
                .orElseThrow(RefreshSessionTokensService::sessionUnauthorized);
    }

    private void persistRotation(Session rotated, RefreshToken presented, Instant now) {
        boolean rotatedSingleRow = sessions.rotateRefreshToken(
                rotated.id(), presented, rotated.refreshToken(), rotated.expiresAt(), now);
        if (!rotatedSingleRow) {
            throw sessionUnauthorized();
        }
    }

    private static UnauthorizedException sessionUnauthorized() {
        return Unauthorized.of(AuthFailureReason.SESSION);
    }
}
