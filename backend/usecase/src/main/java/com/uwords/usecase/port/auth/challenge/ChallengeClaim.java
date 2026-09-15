package com.uwords.usecase.port.auth.challenge;

import java.util.Optional;

public record ChallengeClaim(Optional<StoredChallenge> challenge, boolean exhausted) {

    public static ChallengeClaim of(StoredChallenge challenge) {
        return new ChallengeClaim(Optional.of(challenge), false);
    }

    public static ChallengeClaim missing() {
        return new ChallengeClaim(Optional.empty(), false);
    }

    public static ChallengeClaim exhaustedNow() {
        return new ChallengeClaim(Optional.empty(), true);
    }
}
