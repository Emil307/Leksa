package com.uwords.domain.auth.challenge;

import com.uwords.domain.common.ValidationException;
import java.util.LinkedHashMap;
import java.util.Map;

public class ChallengeStrategyRegistry {

    private final Map<ChallengeType, ChallengeStrategy> byType;

    public ChallengeStrategyRegistry(Iterable<ChallengeStrategy> strategies) {
        Map<ChallengeType, ChallengeStrategy> registered = new LinkedHashMap<>();
        for (ChallengeStrategy strategy : strategies) {
            registered.put(strategy.challengeType(), strategy);
        }
        this.byType = Map.copyOf(registered);
    }

    public ChallengeStrategy forType(ChallengeType challengeType) {
        ChallengeStrategy strategy = byType.get(challengeType);
        if (strategy == null) {
            throw new ValidationException(ChallengeType.UNSUPPORTED_CHALLENGE_TYPE_MESSAGE);
        }
        return strategy;
    }
}
