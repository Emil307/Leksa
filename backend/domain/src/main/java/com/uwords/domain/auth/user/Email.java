package com.uwords.domain.auth.user;

import com.uwords.domain.common.ValidationException;
import java.nio.charset.StandardCharsets;
import java.text.Normalizer;
import java.util.Locale;
import java.util.regex.Pattern;

public record Email(String value) {

    public static final int MAX_OCTETS = 254;
    public static final String MASKED_LOCAL_PART = "***";

    private static final Pattern ADDRESS_PATTERN = Pattern.compile(
            "[^@\\s]+@[^@\\s.]+(?:\\.[^@\\s.]+)+", Pattern.UNICODE_CHARACTER_CLASS);
    private static final String REQUIRED_MESSAGE = "Email is required";
    private static final String TOO_LONG_MESSAGE = "Email is too long";
    private static final String INVALID_MESSAGE = "Email is not a valid address";

    public static Email of(String raw) {
        if (raw == null || raw.strip().isEmpty()) {
            throw new ValidationException(REQUIRED_MESSAGE);
        }
        String normalized = Normalizer.normalize(raw.strip(), Normalizer.Form.NFC).toLowerCase(Locale.ROOT);
        Email candidate = new Email(normalized);
        if (candidate.octetLength() > MAX_OCTETS) {
            throw new ValidationException(TOO_LONG_MESSAGE);
        }
        if (!ADDRESS_PATTERN.matcher(normalized).matches()) {
            throw new ValidationException(INVALID_MESSAGE);
        }
        return candidate;
    }

    public int octetLength() {
        return value.getBytes(StandardCharsets.UTF_8).length;
    }

    public String masked() {
        int separator = value.indexOf('@');
        if (separator < 0) {
            return MASKED_LOCAL_PART;
        }
        String local = value.substring(0, separator);
        String domain = value.substring(separator + 1);
        return local.substring(0, Math.min(1, local.length())) + MASKED_LOCAL_PART + "@" + domain;
    }

    @Override
    public String toString() {
        return "<masked>";
    }
}
