package com.uwords.domain.auth.challenge;

import com.uwords.domain.common.ValidationException;
import java.nio.charset.StandardCharsets;

public record PresentedSecret(String value) {

    public static final int MAX_PRESENTED_SECRET_OCTETS = 512;
    public static final String PRESENTED_SECRET_REQUIRED_MESSAGE = "Secret is required";
    public static final String PRESENTED_SECRET_TOO_LONG_MESSAGE = "Secret is too long";

    public static PresentedSecret of(Object raw) {
        return switch (raw) {
            case String text when !text.strip().isEmpty() -> fromText(text);
            case null, default -> throw new ValidationException(PRESENTED_SECRET_REQUIRED_MESSAGE);
        };
    }

    private static PresentedSecret fromText(String text) {
        if (text.getBytes(StandardCharsets.UTF_8).length > MAX_PRESENTED_SECRET_OCTETS) {
            throw new ValidationException(PRESENTED_SECRET_TOO_LONG_MESSAGE);
        }
        return new PresentedSecret(text);
    }

    @Override
    public String toString() {
        return "<redacted>";
    }
}
