package com.uwords.usecase.testing.statements;

import com.uwords.domain.auth.challenge.ChallengeStrategy;
import com.uwords.domain.auth.challenge.ChallengeStrategyRegistry;
import com.uwords.domain.auth.challenge.ChallengeType;
import com.uwords.usecase.port.auth.session.SessionIssuancePort;
import com.uwords.usecase.service.auth.StartAuthChallengeService;
import com.uwords.usecase.service.auth.StartChallengeRequest;
import com.uwords.usecase.service.auth.VerifyAuthChallengeService;
import com.uwords.usecase.service.auth.VerifyChallengeRequest;
import com.uwords.usecase.testing.AuthVerifyFixtures;
import com.uwords.usecase.testing.ChallengeStartFixtures;
import com.uwords.usecase.testing.EmailCodeFixtures;
import com.uwords.usecase.testing.fakes.FakeChallengeVerificationStore;
import com.uwords.usecase.testing.fakes.FakeIdGenerator;
import com.uwords.usecase.testing.fakes.FakeNotificationQueue;
import com.uwords.usecase.testing.fakes.FixedClock;
import com.uwords.usecase.testing.fakes.StubAccessTokenIssuer;
import com.uwords.usecase.testing.fakes.StubCodeGenerator;
import com.uwords.usecase.testing.fakes.StubRefreshTokenGenerator;
import com.uwords.usecase.testing.recording.CallJournal;
import java.util.List;
import java.util.UUID;

public class EmailCodeLogin {

    private final ChallengeStrategyRegistry strategies = new ChallengeStrategyRegistry(
            List.<ChallengeStrategy>of(
                    EmailCodeFixtures.buildEmailCodeStrategy(
                            new StubCodeGenerator(EmailCodeFixtures.CODE))));
    private final StartAuthChallengeService starts;
    private final VerifyAuthChallengeService logins;

    public EmailCodeLogin(
            CallJournal journal,
            SessionIssuancePort sessions,
            FixedClock clock,
            StubRefreshTokenGenerator refreshTokens,
            StubAccessTokenIssuer accessTokens) {
        FakeChallengeVerificationStore challenges = new FakeChallengeVerificationStore(journal);
        FakeIdGenerator ids = new FakeIdGenerator(RefreshSessionData.IDS);
        this.starts = ChallengeStartFixtures.buildStartChallengeService(
                strategies, challenges, new FakeNotificationQueue(journal), clock, ids);
        this.logins = new VerifyAuthChallengeService(
                strategies,
                challenges,
                sessions,
                refreshTokens,
                accessTokens,
                clock,
                ids,
                ChallengeStartFixtures.CHALLENGE_POLICY,
                AuthVerifyFixtures.SESSION_POLICY);
    }

    public String signInAndTakeRefreshToken() {
        UUID challengeId = starts.start(new StartChallengeRequest(
                        EmailCodeFixtures.EMAIL, ChallengeType.EMAIL_CODE.value()))
                .challengeId();
        return logins.verify(new VerifyChallengeRequest(String.valueOf(challengeId), EmailCodeFixtures.CODE))
                .refreshToken();
    }
}
