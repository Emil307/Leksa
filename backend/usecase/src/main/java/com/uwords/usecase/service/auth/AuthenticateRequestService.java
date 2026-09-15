package com.uwords.usecase.service.auth;

import com.uwords.domain.auth.failure.AuthFailureReason;
import com.uwords.domain.auth.failure.Unauthorized;
import com.uwords.domain.auth.session.ActiveSession;
import com.uwords.domain.auth.session.BearerCredential;
import com.uwords.domain.auth.session.VerifiedAccessToken;
import com.uwords.domain.common.UnavailableException;
import com.uwords.usecase.AuthenticatedCaller;
import com.uwords.usecase.port.auth.session.AccessTokenDecoderPort;
import com.uwords.usecase.port.auth.session.ActiveSessionRepositoryPort;
import com.uwords.usecase.port.system.ClockPort;
import java.time.Instant;
import java.util.Optional;
import java.util.UUID;
import org.springframework.stereotype.Service;

@Service
public class AuthenticateRequestService {

    private final AccessTokenDecoderPort decoder;
    private final ActiveSessionRepositoryPort sessions;
    private final ClockPort clock;

    public AuthenticateRequestService(
            AccessTokenDecoderPort decoder, ActiveSessionRepositoryPort sessions, ClockPort clock) {
        this.decoder = decoder;
        this.sessions = sessions;
        this.clock = clock;
    }

    public AuthenticatedCaller authenticate(String authorizationHeader) {
        BearerCredential credential = BearerCredential.of(authorizationHeader);
        VerifiedAccessToken token = VerifiedAccessToken.of(decoder.decode(credential.token()));
        Instant now = clock.now();
        if (token.isExpiredAt(now)) {
            throw Unauthorized.of(AuthFailureReason.SESSION);
        }
        findSession(token.sessionId())
                .filter(session -> session.authorizes(token, now))
                .orElseThrow(() -> Unauthorized.of(AuthFailureReason.SESSION));
        return new AuthenticatedCaller(token.subject(), token.sessionId());
    }

    private Optional<ActiveSession> findSession(UUID sessionId) {
        try {
            return sessions.findById(sessionId);
        } catch (UnavailableException unreachable) {
            throw Unauthorized.of(AuthFailureReason.STORAGE);
        }
    }
}
