package com.uwords.usecase.testing.fakes;

import com.uwords.usecase.port.system.HealthCheckPort;

public class FakeHealthCheck implements HealthCheckPort {

    public boolean reachable = true;

    @Override
    public boolean ping() {
        return reachable;
    }
}
