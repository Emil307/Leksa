package com.uwords.domain.auth.challenge;

public interface ChallengeSecret {

    String value();

    boolean matches(String raw);
}
