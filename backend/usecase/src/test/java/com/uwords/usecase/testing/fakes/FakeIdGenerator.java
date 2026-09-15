package com.uwords.usecase.testing.fakes;

import com.uwords.usecase.port.system.IdGeneratorPort;
import java.util.ArrayDeque;
import java.util.Deque;
import java.util.List;
import java.util.UUID;

public class FakeIdGenerator implements IdGeneratorPort {

    private final Deque<UUID> remaining;

    public FakeIdGenerator(List<UUID> ids) {
        this.remaining = new ArrayDeque<>(ids);
    }

    @Override
    public UUID newId() {
        return PreparedValues.take(remaining, "FakeIdGenerator");
    }
}
