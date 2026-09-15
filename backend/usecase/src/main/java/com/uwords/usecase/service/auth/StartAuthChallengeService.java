package com.uwords.usecase.service.auth;

import com.uwords.domain.auth.challenge.Challenge;
import com.uwords.domain.auth.challenge.ChallengePolicy;
import com.uwords.domain.auth.challenge.ChallengeSecret;
import com.uwords.domain.auth.challenge.ChallengeStrategy;
import com.uwords.domain.auth.challenge.ChallengeStrategyRegistry;
import com.uwords.domain.auth.challenge.ChallengeSubject;
import com.uwords.domain.auth.challenge.ChallengeType;
import com.uwords.domain.common.ConflictException;
import com.uwords.domain.common.UnavailableException;
import com.uwords.domain.notifications.OutboundNotification;
import com.uwords.usecase.port.auth.challenge.ChallengeStorePort;
import com.uwords.usecase.port.auth.challenge.CooldownAcquisition;
import com.uwords.usecase.port.notifications.NotificationQueuePort;
import com.uwords.usecase.port.system.ClockPort;
import com.uwords.usecase.port.system.IdGeneratorPort;
import java.time.Instant;
import java.util.Map;
import java.util.UUID;
import org.springframework.stereotype.Service;

@Service
public class StartAuthChallengeService {

    public static final String COOLDOWN_MESSAGE = "Challenge start is on cooldown";
    public static final String RETRY_AFTER_KEY = "retryAfterSeconds";
    public static final String UNAVAILABLE_MESSAGE = "Challenge start could not be queued";

    private final ChallengeStrategyRegistry strategies;
    private final ChallengeStorePort challenges;
    private final NotificationQueuePort notifications;
    private final ClockPort clock;
    private final IdGeneratorPort ids;
    private final ChallengePolicy policy;

    public StartAuthChallengeService(
            ChallengeStrategyRegistry strategies,
            ChallengeStorePort challenges,
            NotificationQueuePort notifications,
            ClockPort clock,
            IdGeneratorPort ids,
            ChallengePolicy policy) {
        this.strategies = strategies;
        this.challenges = challenges;
        this.notifications = notifications;
        this.clock = clock;
        this.ids = ids;
        this.policy = policy;
    }

    public StartedChallenge start(StartChallengeRequest request) {
        ChallengeType challengeType = request.parsedType();
        ChallengeStrategy strategy = strategies.forType(challengeType);
        ChallengeSubject subject = strategy.subjectOf(request.credential());
        guardCooldown(challengeType, subject);
        Challenge challenge = createChallenge(challengeType, subject, strategy.issueSecret());
        challenges.swapChallenge(challenge);
        enqueueOrDiscard(challenge, strategy.notificationFor(challenge, subject));
        return StartedChallenge.of(challenge);
    }

    private void guardCooldown(ChallengeType challengeType, ChallengeSubject subject) {
        CooldownAcquisition acquisition = challenges.acquireCooldown(
                challengeType.value(), subject.uniquenessKey(), policy.resendCooldownSeconds());
        if (!acquisition.acquired()) {
            throw new ConflictException(
                    COOLDOWN_MESSAGE, Map.of(RETRY_AFTER_KEY, acquisition.retryAfterSeconds()));
        }
    }

    private Challenge createChallenge(
            ChallengeType challengeType, ChallengeSubject subject, ChallengeSecret secret) {
        UUID challengeId = ids.newId();
        Instant now = clock.now();
        return Challenge.create(challengeId, challengeType, subject, secret, now, policy);
    }

    private void enqueueOrDiscard(Challenge challenge, OutboundNotification notification) {
        try {
            notifications.enqueue(notification);
        } catch (RuntimeException failure) {
            challenges.discardStartedChallenge(challenge);
            throw new UnavailableException(UNAVAILABLE_MESSAGE, Map.of(), false);
        }
    }
}
