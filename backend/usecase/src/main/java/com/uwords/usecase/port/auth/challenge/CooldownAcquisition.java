package com.uwords.usecase.port.auth.challenge;

public record CooldownAcquisition(boolean acquired, long retryAfterSeconds) {

    public static CooldownAcquisition granted() {
        return new CooldownAcquisition(true, 0);
    }

    public static CooldownAcquisition denied(long retryAfterSeconds) {
        return new CooldownAcquisition(false, retryAfterSeconds);
    }
}
