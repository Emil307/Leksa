package com.uwords.domain.auth.session;

import com.uwords.domain.auth.failure.AuthFailureReason;
import com.uwords.domain.auth.failure.Unauthorized;
import java.nio.charset.StandardCharsets;
import java.util.Locale;
import java.util.regex.Pattern;

public record BearerCredential(String token) {

    public static final int MAX_AUTHORIZATION_HEADER_OCTETS = 4096;
    public static final String BEARER_SCHEME = "Bearer";

    private static final Pattern WHITESPACE = Pattern.compile("\\s+", Pattern.UNICODE_CHARACTER_CLASS);
    private static final int SCHEME_AND_TOKEN = 2;

    public static BearerCredential of(String headerValue) {
        if (headerValue == null) {
            throw Unauthorized.of(AuthFailureReason.HEADER);
        }
        if (headerValue.getBytes(StandardCharsets.UTF_8).length > MAX_AUTHORIZATION_HEADER_OCTETS) {
            throw Unauthorized.of(AuthFailureReason.HEADER);
        }
        String[] parts = WHITESPACE.split(headerValue.strip());
        if (parts.length != SCHEME_AND_TOKEN) {
            throw Unauthorized.of(AuthFailureReason.HEADER);
        }
        if (!parts[0].toLowerCase(Locale.ROOT).equals(BEARER_SCHEME.toLowerCase(Locale.ROOT))) {
            throw Unauthorized.of(AuthFailureReason.HEADER);
        }
        return new BearerCredential(parts[1]);
    }

    @Override
    public String toString() {
        return "BearerCredential(token=<redacted>)";
    }
}
