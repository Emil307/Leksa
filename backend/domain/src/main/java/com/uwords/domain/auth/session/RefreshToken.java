package com.uwords.domain.auth.session;

import com.uwords.domain.common.ValidationException;
import java.nio.charset.StandardCharsets;

public record RefreshToken(String value) {

    public static final int MAX_TOKEN_BYTES = 512;
    public static final String TOKEN_REQUIRED_MESSAGE = "Refresh token is required";
    public static final String TOKEN_INVALID_MESSAGE = "Refresh token is not valid";

    private static final char MIN_PRINTABLE = 0x20;
    private static final char MAX_PRINTABLE = 0x7E;

    public static RefreshToken of(String raw) {
        if (raw == null || raw.strip().isEmpty()) {
            throw new ValidationException(TOKEN_REQUIRED_MESSAGE);
        }
        if (raw.getBytes(StandardCharsets.UTF_8).length > MAX_TOKEN_BYTES) {
            throw new ValidationException(TOKEN_INVALID_MESSAGE);
        }
        if (!isPrintableAscii(raw)) {
            throw new ValidationException(TOKEN_INVALID_MESSAGE);
        }
        return new RefreshToken(raw);
    }

    public boolean matches(RefreshToken other) {
        if (value.length() != other.value.length()) {
            return false;
        }
        int difference = 0;
        for (int index = 0; index < value.length(); index++) {
            difference |= value.charAt(index) ^ other.value.charAt(index);
        }
        return difference == 0;
    }

    private static boolean isPrintableAscii(String raw) {
        for (int index = 0; index < raw.length(); index++) {
            char character = raw.charAt(index);
            if (character < MIN_PRINTABLE || character > MAX_PRINTABLE) {
                return false;
            }
        }
        return true;
    }

    @Override
    public String toString() {
        return "<redacted>";
    }
}
