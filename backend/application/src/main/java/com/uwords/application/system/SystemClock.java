package com.uwords.application.system;

import com.uwords.usecase.port.system.ClockPort;
import java.time.Clock;
import java.time.Instant;
import org.springframework.stereotype.Component;

@Component
public class SystemClock implements ClockPort {

    private final Clock clock;

    public SystemClock() {
        this(Clock.systemUTC());
    }

    public SystemClock(Clock clock) {
        this.clock = clock;
    }

    @Override
    public Instant now() {
        return clock.instant();
    }
}
