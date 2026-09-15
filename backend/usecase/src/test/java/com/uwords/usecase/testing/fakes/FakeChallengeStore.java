package com.uwords.usecase.testing.fakes;

import com.uwords.domain.auth.challenge.Challenge;
import com.uwords.usecase.port.auth.challenge.ChallengeStorePort;
import com.uwords.usecase.port.auth.challenge.CooldownAcquisition;
import com.uwords.usecase.testing.recording.CallJournal;
import com.uwords.usecase.testing.recording.CooldownArguments;

public class FakeChallengeStore implements ChallengeStorePort {

    public static final String ACQUIRE_COOLDOWN = "acquire_cooldown";
    public static final String SWAP_CHALLENGE = "swap_challenge";
    public static final String DISCARD_STARTED_CHALLENGE = "discard_started_challenge";

    protected final CallJournal journal;

    private CooldownAcquisition acquisition = CooldownAcquisition.granted();

    public FakeChallengeStore(CallJournal journal) {
        this.journal = journal;
    }

    public void answerCooldownWith(CooldownAcquisition acquisition) {
        this.acquisition = acquisition;
    }

    @Override
    public CooldownAcquisition acquireCooldown(
            String challengeType, String uniquenessKey, long cooldownSeconds) {
        journal.record(
                ACQUIRE_COOLDOWN, new CooldownArguments(challengeType, uniquenessKey, cooldownSeconds));
        return acquisition;
    }

    @Override
    public void swapChallenge(Challenge challenge) {
        journal.record(SWAP_CHALLENGE, challenge);
    }

    @Override
    public void discardStartedChallenge(Challenge challenge) {
        journal.record(DISCARD_STARTED_CHALLENGE, challenge);
    }
}
