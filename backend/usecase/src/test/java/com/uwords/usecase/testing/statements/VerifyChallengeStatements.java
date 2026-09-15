package com.uwords.usecase.testing.statements;

import static org.assertj.core.api.Assertions.assertThat;

import com.uwords.domain.auth.challenge.ChallengeStrategy;
import com.uwords.domain.auth.challenge.ChallengeStrategyRegistry;
import com.uwords.domain.auth.challenge.ChallengeType;
import com.uwords.usecase.service.auth.StartAuthChallengeService;
import com.uwords.usecase.service.auth.StartChallengeRequest;
import com.uwords.usecase.service.auth.VerifiedSession;
import com.uwords.usecase.service.auth.VerifyAuthChallengeService;
import com.uwords.usecase.service.auth.VerifyChallengeRequest;
import com.uwords.usecase.testing.AuthVerifyFixtures;
import com.uwords.usecase.testing.ChallengeStartFixtures;
import com.uwords.usecase.testing.EmailCodeFixtures;
import com.uwords.usecase.testing.fakes.FakeChallengeVerificationStore;
import com.uwords.usecase.testing.fakes.FixedClock;
import com.uwords.usecase.testing.fakes.FakeIdGenerator;
import com.uwords.usecase.testing.fakes.FakeNotificationQueue;
import com.uwords.usecase.testing.fakes.FakeSessionIssuance;
import com.uwords.usecase.testing.fakes.StubAccessTokenIssuer;
import com.uwords.usecase.testing.fakes.StubCodeGenerator;
import com.uwords.usecase.testing.fakes.StubRefreshTokenGenerator;
import com.uwords.usecase.testing.recording.CallJournal;
import com.uwords.usecase.testing.recording.JournalEntry;
import java.util.List;
import java.util.Map;
import java.util.UUID;

public class VerifyChallengeStatements {

    private final CallJournal journal = new CallJournal();
    private final FakeChallengeVerificationStore challenges = new FakeChallengeVerificationStore(journal);
    private final FakeSessionIssuance sessions = new FakeSessionIssuance(journal);
    private final ChallengeStrategyRegistry strategies = new ChallengeStrategyRegistry(
            List.<ChallengeStrategy>of(
                    EmailCodeFixtures.buildEmailCodeStrategy(
                            new StubCodeGenerator(EmailCodeFixtures.CODE))));
    private final FakeIdGenerator ids = new FakeIdGenerator(AuthVerifyFixtures.IDS);
    private final FixedClock clock = new FixedClock(EmailCodeFixtures.NOW);
    private final StartAuthChallengeService starts = buildStartService();
    private final VerifyAuthChallengeService service = buildVerifyService();

    private UUID registeredUserId;
    private UUID firstSessionId;
    private UUID challengeId;
    private VerifiedSession verified;

    public void givenRegisteredUserHoldsAFreshCode() {
        VerifiedSession earlier = service.verify(request(requestCode()));
        registeredUserId = earlier.userId();
        firstSessionId = earlier.sessionId();
        challengeId = requestCode();
    }

    public void whenUserSendsTheCorrectCode() {
        verified = service.verify(request(challengeId));
    }

    public void assertSessionBelongsToTheExistingUser() {
        assertThat(registeredUserId).isEqualTo(AuthVerifyFixtures.USER_ID);
        assertThat(verified.userId()).isEqualTo(AuthVerifyFixtures.USER_ID);
    }

    public void assertNoNewUserIsCreated() {
        assertThat(sessions.users)
                .isEqualTo(Map.of(AuthVerifyFixtures.ACCOUNT, AuthVerifyFixtures.USER_ID));
        assertThat(sessions.issued).isEqualTo(AuthVerifyFixtures.EXPECTED_ISSUED_RECORDS);
        assertThat(payloads(FakeSessionIssuance.ISSUE_SESSION))
                .isEqualTo(AuthVerifyFixtures.EXPECTED_ISSUANCE_REQUESTS);
    }

    public void assertSessionCarriesItsOwnIdentityAndTokens() {
        assertThat(firstSessionId).isEqualTo(AuthVerifyFixtures.FIRST_SESSION_ID);
        assertThat(verified).isEqualTo(AuthVerifyFixtures.EXPECTED_VERIFIED_SESSION);
    }

    public void assertAccessTokenIsIssuedForThatUserAndSession() {
        assertThat(payloads(StubAccessTokenIssuer.ISSUE_ACCESS_TOKEN))
                .isEqualTo(AuthVerifyFixtures.EXPECTED_ACCESS_TOKEN_CLAIMS);
    }

    public void assertAttemptIsClaimedBeforeTheChallengeIsRedeemed() {
        assertThat(journal.names()).isEqualTo(AuthVerifyFixtures.EXPECTED_CALL_NAMES);
        assertThat(payloads(FakeChallengeVerificationStore.FIND_CHALLENGE))
                .isEqualTo(AuthVerifyFixtures.EXPECTED_CHALLENGE_IDS);
        assertThat(payloads(FakeChallengeVerificationStore.CLAIM_ATTEMPT))
                .isEqualTo(AuthVerifyFixtures.EXPECTED_CLAIMS);
        assertThat(payloads(FakeChallengeVerificationStore.REDEEM_CHALLENGE))
                .isEqualTo(AuthVerifyFixtures.EXPECTED_CHALLENGE_IDS);
    }

    public void assertRedeemedChallengeIsRememberedForReplay() {
        assertThat(payloads(FakeChallengeVerificationStore.REMEMBER_VERIFICATION))
                .isEqualTo(AuthVerifyFixtures.EXPECTED_REMEMBERED);
        assertThat(challenges.verifications).isEqualTo(AuthVerifyFixtures.EXPECTED_VERIFICATIONS);
        assertThat(challenges.records).isEmpty();
    }

    private List<Object> payloads(String call) {
        int offset = AuthVerifyFixtures.VERIFY_CALL_NAMES.indexOf(call);
        List<JournalEntry> calls = journal.calls();
        List<JournalEntry> recorded =
                AuthVerifyFixtures.VERIFY_STARTS.stream().map(start -> calls.get(start + offset)).toList();
        assertThat(recorded.stream().map(JournalEntry::name).toList()).isEqualTo(List.of(call, call));
        return recorded.stream().map(JournalEntry::payload).toList();
    }

    private UUID requestCode() {
        return starts.start(new StartChallengeRequest(
                        EmailCodeFixtures.EMAIL, ChallengeType.EMAIL_CODE.value()))
                .challengeId();
    }

    private VerifyChallengeRequest request(UUID challenge) {
        return new VerifyChallengeRequest(String.valueOf(challenge), EmailCodeFixtures.CODE);
    }

    private StartAuthChallengeService buildStartService() {
        return ChallengeStartFixtures.buildStartChallengeService(
                strategies, challenges, new FakeNotificationQueue(journal), clock, ids);
    }

    private VerifyAuthChallengeService buildVerifyService() {
        return new VerifyAuthChallengeService(
                strategies,
                challenges,
                sessions,
                new StubRefreshTokenGenerator(AuthVerifyFixtures.REFRESH_TOKENS),
                new StubAccessTokenIssuer(journal, AuthVerifyFixtures.ACCESS_TOKENS),
                clock,
                ids,
                ChallengeStartFixtures.CHALLENGE_POLICY,
                AuthVerifyFixtures.SESSION_POLICY);
    }
}
