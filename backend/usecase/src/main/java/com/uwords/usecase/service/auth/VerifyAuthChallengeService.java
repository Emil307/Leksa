package com.uwords.usecase.service.auth;

import com.uwords.domain.auth.challenge.ChallengeId;
import com.uwords.domain.auth.challenge.ChallengePolicy;
import com.uwords.domain.auth.challenge.ChallengeStrategy;
import com.uwords.domain.auth.challenge.ChallengeStrategyRegistry;
import com.uwords.domain.auth.challenge.ChallengeVerification;
import com.uwords.domain.auth.challenge.PresentedSecret;
import com.uwords.domain.auth.session.AccessTokenClaims;
import com.uwords.domain.auth.session.RefreshToken;
import com.uwords.domain.auth.session.SessionPolicy;
import com.uwords.domain.common.UnauthorizedException;
import com.uwords.usecase.port.auth.challenge.ChallengeClaim;
import com.uwords.usecase.port.auth.challenge.ChallengeVerificationStorePort;
import com.uwords.usecase.port.auth.challenge.StoredChallenge;
import com.uwords.usecase.port.auth.session.AccessTokenIssuerPort;
import com.uwords.usecase.port.auth.session.IssuedSessionRecord;
import com.uwords.usecase.port.auth.session.RefreshTokenGeneratorPort;
import com.uwords.usecase.port.auth.session.SessionIssuancePort;
import com.uwords.usecase.port.auth.session.SessionIssuanceRequest;
import com.uwords.usecase.port.system.ClockPort;
import com.uwords.usecase.port.system.IdGeneratorPort;
import java.time.Instant;
import java.util.Map;
import java.util.UUID;
import org.springframework.stereotype.Service;

@Service
public class VerifyAuthChallengeService {

    public static final String MISMATCHED_SECRET_MESSAGE = "Presented secret does not match the challenge";

    private final ChallengeStrategyRegistry strategies;
    private final ChallengeVerificationStorePort challenges;
    private final SessionIssuancePort sessions;
    private final RefreshTokenGeneratorPort refreshTokens;
    private final AccessTokenIssuerPort accessTokens;
    private final ClockPort clock;
    private final IdGeneratorPort ids;
    private final ChallengePolicy challengePolicy;
    private final SessionPolicy sessionPolicy;

    public VerifyAuthChallengeService(
            ChallengeStrategyRegistry strategies,
            ChallengeVerificationStorePort challenges,
            SessionIssuancePort sessions,
            RefreshTokenGeneratorPort refreshTokens,
            AccessTokenIssuerPort accessTokens,
            ClockPort clock,
            IdGeneratorPort ids,
            ChallengePolicy challengePolicy,
            SessionPolicy sessionPolicy) {
        this.strategies = strategies;
        this.challenges = challenges;
        this.sessions = sessions;
        this.refreshTokens = refreshTokens;
        this.accessTokens = accessTokens;
        this.clock = clock;
        this.ids = ids;
        this.challengePolicy = challengePolicy;
        this.sessionPolicy = sessionPolicy;
    }

    public VerifiedSession verify(VerifyChallengeRequest request) {
        ChallengeId challengeId = ChallengeId.of(request.challengeId());
        PresentedSecret presented = PresentedSecret.of(request.code());
        ChallengeStrategy strategy = strategyFor(challengeId);
        StoredChallenge claimed = redeem(challengeId, strategy, presented);
        Instant now = clock.now();
        IssuedSessionTokens tokens = issueSession(claimed, strategy, now);
        remember(claimed, tokens.issued(), now);
        return verified(tokens.issued(), tokens.refreshToken(), now);
    }

    private ChallengeStrategy strategyFor(ChallengeId challengeId) {
        StoredChallenge stored = challenges.findChallenge(challengeId.value()).orElseThrow();
        return strategies.forType(stored.challengeType());
    }

    private StoredChallenge redeem(
            ChallengeId challengeId, ChallengeStrategy strategy, PresentedSecret presented) {
        strategy.restoreSecret(presented.value());
        StoredChallenge claimed = claim(challengeId, strategy, presented);
        challenges.redeemChallenge(challengeId.value());
        return claimed;
    }

    private StoredChallenge claim(
            ChallengeId challengeId, ChallengeStrategy strategy, PresentedSecret presented) {
        ChallengeClaim claim = challenges.claimAttempt(challengeId.value(), challengePolicy.maxAttempts());
        StoredChallenge claimed = claim.challenge().orElseThrow();
        if (!strategy.restoreSecret(claimed.secretValue()).matches(presented.value())) {
            throw new UnauthorizedException(MISMATCHED_SECRET_MESSAGE, Map.of(), false);
        }
        return claimed;
    }

    private IssuedSessionTokens issueSession(
            StoredChallenge claimed, ChallengeStrategy strategy, Instant now) {
        RefreshToken refreshToken = RefreshToken.of(refreshTokens.generate());
        SessionIssuanceRequest request = issuanceRequest(claimed, strategy, refreshToken, now);
        IssuedSessionRecord issued = sessions.issueSession(request);
        return new IssuedSessionTokens(issued, refreshToken);
    }

    private SessionIssuanceRequest issuanceRequest(
            StoredChallenge claimed, ChallengeStrategy strategy, RefreshToken refreshToken, Instant now) {
        UUID candidateUserId = ids.newId();
        UUID sessionId = ids.newId();
        return new SessionIssuanceRequest(
                strategy.accountFor(claimed.uniquenessKey()),
                candidateUserId,
                sessionId,
                refreshToken,
                SessionPolicy.truncate(now),
                sessionPolicy.refreshExpiryAt(now));
    }

    private void remember(StoredChallenge claimed, IssuedSessionRecord issued, Instant now) {
        ChallengeVerification verification = new ChallengeVerification(
                claimed.id(), issued.userId(), issued.sessionId());
        challenges.rememberVerification(
                verification, challengePolicy.replayTtlSeconds(now, claimed.expiresAt()));
    }

    private VerifiedSession verified(IssuedSessionRecord issued, RefreshToken refreshToken, Instant now) {
        UUID tokenId = ids.newId();
        AccessTokenClaims claims = AccessTokenClaims.of(
                issued.userId(), issued.sessionId(), tokenId, now, sessionPolicy);
        String accessToken = accessTokens.issue(claims);
        return new VerifiedSession(issued.userId(), issued.sessionId(), refreshToken.value(), accessToken);
    }
}
