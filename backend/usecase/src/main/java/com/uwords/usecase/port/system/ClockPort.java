package com.uwords.usecase.port.system;

import java.time.Instant;

public interface ClockPort {

    Instant now();
}
