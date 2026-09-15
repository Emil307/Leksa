package com.uwords.usecase.port.auth.challenge;

import com.uwords.domain.auth.challenge.Challenge;

public interface ChallengeStorePort {

    CooldownAcquisition acquireCooldown(String challengeType, String uniquenessKey, long cooldownSeconds);

    void swapChallenge(Challenge challenge);

    void discardStartedChallenge(Challenge challenge);
}
