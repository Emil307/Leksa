package com.uwords.usecase.testing.statements;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.catchThrowable;

import com.uwords.domain.auth.challenge.Challenge;
import com.uwords.domain.auth.challenge.ChallengeStrategy;
import com.uwords.domain.auth.challenge.ChallengeStrategyRegistry;
import com.uwords.domain.auth.challenge.ChallengeType;
import com.uwords.domain.common.BaseDomainException;
import com.uwords.domain.common.ErrorCode;
import com.uwords.domain.common.UnavailableException;
import com.uwords.domain.notifications.OutboundEmail;
import com.uwords.usecase.service.auth.StartAuthChallengeService;
import com.uwords.usecase.service.auth.StartChallengeRequest;
import com.uwords.usecase.service.auth.StartedChallenge;
import com.uwords.usecase.testing.ChallengeStartFixtures;
import com.uwords.usecase.testing.EmailCodeFixtures;
import com.uwords.usecase.testing.fakes.FakeChallengeStore;
import com.uwords.usecase.testing.fakes.FixedClock;
import com.uwords.usecase.testing.fakes.FakeIdGenerator;
import com.uwords.usecase.testing.fakes.FakeNotificationQueue;
import com.uwords.usecase.testing.fakes.StubCodeGenerator;
import com.uwords.usecase.testing.recording.CallJournal;
import java.util.List;
import java.util.Map;

public class StartChallengeStatements {

    private final CallJournal journal = new CallJournal();
    private final FakeNotificationQueue queue = new FakeNotificationQueue(journal);
    private final StubCodeGenerator codes = new StubCodeGenerator(EmailCodeFixtures.CODE);
    private final StartAuthChallengeService service = buildService();

    private StartedChallenge started;
    private BaseDomainException failure;

    public void givenNotificationQueueRejectsRequests() {
        queue.failWith(new RuntimeException(StartChallengeFixtures.QUEUE_FAILURE_MESSAGE));
    }

    public void whenClientRequestsCodeToOwnEmail() {
        started = service.start(request());
    }

    public void whenClientRequestsCodeAndStartFails() {
        Throwable thrown = catchThrowable(() -> started = service.start(request()));
        assertThat(thrown).isInstanceOf(BaseDomainException.class);
        failure = (BaseDomainException) thrown;
    }

    public void assertStartedChallengeCarriesIdentityAndExpiry() {
        assertThat(started).isEqualTo(StartChallengeFixtures.EXPECTED_STARTED_CHALLENGE);
    }

    public void assertExactlyOneReadyRequestIsQueued() {
        assertThat(queue.messages).isEqualTo(List.of(StartChallengeFixtures.EXPECTED_EMAIL));
    }

    public void assertQueuedCodeIsTheIssuedChallengeSecret() {
        assertThat(codes.requestedLengths).isEqualTo(List.of(EmailCodeFixtures.CODE_LENGTH));
        Challenge stored = (Challenge) journal.payloadOf(FakeChallengeStore.SWAP_CHALLENGE);
        OutboundEmail queued = (OutboundEmail) queue.messages.get(0);
        assertThat(queued.variables().get("code")).isEqualTo(stored.secretValue());
    }

    public void assertRequestIsQueuedOnlyAfterChallengeIsStored() {
        assertThat(journal.names()).isEqualTo(List.of(
                FakeChallengeStore.ACQUIRE_COOLDOWN,
                FakeChallengeStore.SWAP_CHALLENGE,
                FakeNotificationQueue.ENQUEUE));
        assertExpectedCooldownAndChallenge();
    }

    public void assertStartedChallengeIsDiscarded() {
        assertThat(journal.names()).isEqualTo(List.of(
                FakeChallengeStore.ACQUIRE_COOLDOWN,
                FakeChallengeStore.SWAP_CHALLENGE,
                FakeNotificationQueue.ENQUEUE,
                FakeChallengeStore.DISCARD_STARTED_CHALLENGE));
        assertExpectedCooldownAndChallenge();
        assertThat(journal.payloadOf(FakeChallengeStore.DISCARD_STARTED_CHALLENGE))
                .isEqualTo(StartChallengeFixtures.EXPECTED_CHALLENGE);
    }

    public void assertNoRequestIsQueued() {
        assertThat(queue.messages).isEmpty();
    }

    public void assertStartIsRefusedAsUnavailable() {
        assertThat(started).isNull();
        assertThat(failure).isInstanceOf(UnavailableException.class);
        assertThat(failure.code()).isEqualTo(ErrorCode.UNAVAILABLE);
        assertThat(failure.getMessage()).isEqualTo(StartChallengeFixtures.UNAVAILABLE_MESSAGE);
        assertThat(failure.payload()).isEqualTo(Map.of());
        assertThat(failure.exposeToUser()).isFalse();
    }

    private void assertExpectedCooldownAndChallenge() {
        assertThat(journal.payloadOf(FakeChallengeStore.ACQUIRE_COOLDOWN))
                .isEqualTo(StartChallengeFixtures.EXPECTED_COOLDOWN_ARGUMENTS);
        assertThat(journal.payloadOf(FakeChallengeStore.SWAP_CHALLENGE))
                .isEqualTo(StartChallengeFixtures.EXPECTED_CHALLENGE);
    }

    private StartChallengeRequest request() {
        return new StartChallengeRequest(EmailCodeFixtures.EMAIL, ChallengeType.EMAIL_CODE.value());
    }

    private StartAuthChallengeService buildService() {
        return ChallengeStartFixtures.buildStartChallengeService(
                new ChallengeStrategyRegistry(
                        List.<ChallengeStrategy>of(EmailCodeFixtures.buildEmailCodeStrategy(codes))),
                new FakeChallengeStore(journal),
                queue,
                new FixedClock(EmailCodeFixtures.NOW),
                new FakeIdGenerator(List.of(StartChallengeFixtures.CHALLENGE_ID)));
    }
}
