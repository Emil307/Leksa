package com.uwords.usecase.testing.fakes;

import com.uwords.usecase.port.auth.session.RefreshTokenGeneratorPort;
import java.util.ArrayDeque;
import java.util.Deque;
import java.util.List;

public class StubRefreshTokenGenerator implements RefreshTokenGeneratorPort {

    private final Deque<String> remaining;

    public StubRefreshTokenGenerator(List<String> tokens) {
        this.remaining = new ArrayDeque<>(tokens);
    }

    @Override
    public String generate() {
        return PreparedValues.take(remaining, "StubRefreshTokenGenerator");
    }
}
