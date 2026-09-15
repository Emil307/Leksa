package com.uwords.usecase.testing.fakes;

import com.uwords.usecase.port.system.ClockPort;
import java.time.Instant;

public class FixedClock implements ClockPort {

    private Instant now;

    public FixedClock(Instant now) {
        this.now = now;
    }

    @Override
    public Instant now() {
        return now;
    }

    public void set(Instant moment) {
        this.now = moment;
    }
}
