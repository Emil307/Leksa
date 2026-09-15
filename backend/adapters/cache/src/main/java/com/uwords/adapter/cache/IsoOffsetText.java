package com.uwords.adapter.cache;

import java.time.Instant;
import java.time.OffsetDateTime;
import java.time.ZoneOffset;
import java.time.format.DateTimeFormatter;
import java.time.temporal.ChronoUnit;

public final class IsoOffsetText {

    public static final String UTC_OFFSET = "+00:00";

    private static final DateTimeFormatter WHOLE_SECONDS = DateTimeFormatter.ofPattern("yyyy-MM-dd'T'HH:mm:ss");
    private static final int NANOS_IN_MICROSECOND = 1000;

    private IsoOffsetText() {
    }

    public static String of(Instant value) {
        OffsetDateTime moment = value.truncatedTo(ChronoUnit.MICROS).atOffset(ZoneOffset.UTC);
        int microseconds = moment.getNano() / NANOS_IN_MICROSECOND;
        if (microseconds == 0) {
            return moment.format(WHOLE_SECONDS) + UTC_OFFSET;
        }
        return moment.format(WHOLE_SECONDS) + "." + String.format("%06d", microseconds) + UTC_OFFSET;
    }

    public static Instant parse(String text) {
        return OffsetDateTime.parse(text).toInstant();
    }
}
