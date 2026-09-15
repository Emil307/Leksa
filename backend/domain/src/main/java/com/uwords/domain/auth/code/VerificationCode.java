package com.uwords.domain.auth.code;

import com.uwords.domain.auth.challenge.ChallengeSecret;
import com.uwords.domain.common.ValidationException;

public record VerificationCode(String value) implements ChallengeSecret {

    public static final String UNEXPECTED_LENGTH_MESSAGE = "Verification code has an unexpected length";
    public static final String DIGITS_ONLY_MESSAGE = "Verification code must contain digits only";

    public static VerificationCode of(String raw, int length) {
        if (raw == null || raw.length() != length) {
            throw new ValidationException(UNEXPECTED_LENGTH_MESSAGE);
        }
        if (!isAsciiDigits(raw)) {
            throw new ValidationException(DIGITS_ONLY_MESSAGE);
        }
        return new VerificationCode(raw);
    }

    @Override
    public boolean matches(String raw) {
        if (raw == null || raw.length() != value.length()) {
            return false;
        }
        int difference = 0;
        for (int index = 0; index < value.length(); index++) {
            difference |= value.charAt(index) ^ raw.charAt(index);
        }
        return difference == 0;
    }

    private static boolean isAsciiDigits(String raw) {
        for (int index = 0; index < raw.length(); index++) {
            char character = raw.charAt(index);
            if (character < '0' || character > '9') {
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
