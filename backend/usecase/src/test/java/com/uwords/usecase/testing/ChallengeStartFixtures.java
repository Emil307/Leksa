package com.uwords.usecase.testing;

import com.uwords.domain.auth.challenge.ChallengePolicy;
import com.uwords.domain.auth.challenge.ChallengeStrategyRegistry;
import com.uwords.usecase.port.auth.challenge.ChallengeStorePort;
import com.uwords.usecase.port.notifications.NotificationQueuePort;
import com.uwords.usecase.port.system.ClockPort;
import com.uwords.usecase.port.system.IdGeneratorPort;
import com.uwords.usecase.service.auth.StartAuthChallengeService;

public final class ChallengeStartFixtures {

    public static final long TTL_SECONDS = 300;
    public static final int MAX_ATTEMPTS = 3;
    public static final long COOLDOWN_SECONDS = 60;
    public static final long REPLAY_WINDOW_SECONDS = 60;

    public static final ChallengePolicy CHALLENGE_POLICY =
            new ChallengePolicy(TTL_SECONDS, MAX_ATTEMPTS, COOLDOWN_SECONDS, REPLAY_WINDOW_SECONDS);

    private ChallengeStartFixtures() {
    }

    public static StartAuthChallengeService buildStartChallengeService(
            ChallengeStrategyRegistry strategies,
            ChallengeStorePort challenges,
            NotificationQueuePort notifications,
            ClockPort clock,
            IdGeneratorPort ids) {
        return new StartAuthChallengeService(
                strategies, challenges, notifications, clock, ids, CHALLENGE_POLICY);
    }
}
