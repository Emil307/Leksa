package com.uwords.domain.common;

import java.util.Optional;
import java.util.UUID;

public final class UuidText {

    private static final int HEX_DIGITS = 32;
    private static final int HALF = 16;
    private static final int RADIX = 16;

    private UuidText() {
    }

    public static Optional<UUID> parse(String raw) {
        if (raw == null) {
            return Optional.empty();
        }
        String digits = stripBraces(raw.replace("urn:", "").replace("uuid:", "")).replace("-", "");
        if (digits.length() != HEX_DIGITS || !isHex(digits)) {
            return Optional.empty();
        }
        return Optional.of(new UUID(
                Long.parseUnsignedLong(digits.substring(0, HALF), RADIX),
                Long.parseUnsignedLong(digits.substring(HALF), RADIX)));
    }

    private static String stripBraces(String value) {
        int start = 0;
        int end = value.length();
        while (start < end && isBrace(value.charAt(start))) {
            start++;
        }
        while (end > start && isBrace(value.charAt(end - 1))) {
            end--;
        }
        return value.substring(start, end);
    }

    private static boolean isBrace(char character) {
        return character == '{' || character == '}';
    }

    private static boolean isHex(String value) {
        for (int index = 0; index < value.length(); index++) {
            if (Character.digit(value.charAt(index), RADIX) < 0) {
                return false;
            }
        }
        return true;
    }
}
