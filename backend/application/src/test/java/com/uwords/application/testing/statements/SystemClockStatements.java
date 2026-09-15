package com.uwords.application.testing.statements;

import static org.assertj.core.api.Assertions.assertThat;

import com.uwords.application.system.SystemClock;
import java.time.Clock;
import java.time.Instant;
import java.time.ZoneOffset;
import java.util.ArrayList;
import java.util.List;

public class SystemClockStatements {

    private static final Instant A_FIXED_INSTANT = Instant.parse("2026-03-14T09:26:53Z");
    private static final ZoneOffset A_FOREIGN_OFFSET = ZoneOffset.ofHours(3);

    private final SystemClock clock = new SystemClock();
    private final List<Instant> readings = new ArrayList<>();

    private Instant takenBefore;
    private Instant takenAfter;
    private Instant readingOfAZonedClock;

    public void whenTheClockIsRead() {
        takenBefore = Instant.now();
        readings.add(clock.now());
        takenAfter = Instant.now();
    }

    public void whenTheClockIsReadTwice() {
        takenBefore = Instant.now();
        readings.add(clock.now());
        readings.add(clock.now());
        takenAfter = Instant.now();
    }

    public void whenAClockOfAForeignZoneIsRead() {
        readingOfAZonedClock =
                new SystemClock(Clock.fixed(A_FIXED_INSTANT, A_FOREIGN_OFFSET)).now();
    }

    public void assertTheReadingIsAZoneIndependentUtcInstant() {
        assertThat(readingOfAZonedClock).isEqualTo(A_FIXED_INSTANT);
    }

    public void assertTheReadingTracksTheRealCurrentInstant() {
        assertThat(readings.get(0)).isBetween(takenBefore, takenAfter);
    }

    public void assertTheReadingsNeverGoBackwards() {
        Instant earlier = readings.get(0);
        Instant later = readings.get(1);
        assertThat(earlier).isBetween(takenBefore, takenAfter);
        assertThat(later).isBetween(earlier, takenAfter);
    }
}
