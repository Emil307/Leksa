package com.uwords.application.testing.statements;

import com.auth0.jwt.JWT;
import com.auth0.jwt.JWTCreator;
import com.auth0.jwt.algorithms.Algorithm;
import java.nio.charset.StandardCharsets;
import java.util.Base64;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.UUID;

public final class AccessTokenData {

    public static final String SECRET = "application-lane-signing-secret-long-enough-for-hs256-and-hs512-x";
    public static final String OTHER_SECRET = "a-completely-different-signing-secret-long-enough-for-hs256-hs512";

    public static final UUID USER_ID = UUID.fromString("11111111-1111-4111-8111-111111111111");
    public static final UUID SESSION_ID = UUID.fromString("22222222-2222-4222-8222-222222222222");
    public static final UUID TOKEN_ID = UUID.fromString("33333333-3333-4333-8333-333333333333");
    public static final UUID OTHER_TOKEN_ID = UUID.fromString("44444444-4444-4444-8444-444444444444");

    public static final long FAR_FUTURE_EXPIRY = 4102444800L;
    public static final long LONG_PAST_EXPIRY = 1L;
    public static final String API_AUDIENCE = "uwords-api";
    public static final String OTHER_AUDIENCE = "somebody-else";

    public static final String UNKNOWN_CLAIM = "unknown";
    public static final String UNKNOWN_CLAIM_VALUE = "ignored-by-the-decoder";

    public static final String MALFORMED_TOKEN = "not.a.jwt";
    public static final String TAMPERED_SIGNATURE_SUFFIX = "xy";

    private static final String UNSIGNED_HEADER = "{\"alg\":\"none\",\"typ\":\"JWT\"}";

    private AccessTokenData() {
    }

    public static Map<String, Object> claimsOf(UUID tokenId, long expiresAt, String audience) {
        Map<String, Object> claims = new LinkedHashMap<>();
        claims.put("sub", USER_ID.toString());
        claims.put("sid", SESSION_ID.toString());
        claims.put("jti", tokenId.toString());
        claims.put("exp", expiresAt);
        claims.put("aud", audience);
        return claims;
    }

    public static Map<String, Object> claimsOf(long expiresAt, String audience) {
        return claimsOf(TOKEN_ID, expiresAt, audience);
    }

    public static Map<String, Object> claimsOf(UUID tokenId) {
        return claimsOf(tokenId, FAR_FUTURE_EXPIRY, API_AUDIENCE);
    }

    public static Map<String, Object> claimsOf() {
        return claimsOf(TOKEN_ID);
    }

    public static String signed(Map<String, Object> claims, Algorithm algorithm) {
        JWTCreator.Builder builder = JWT.create();
        claims.forEach((name, value) -> add(builder, name, value));
        return builder.sign(algorithm);
    }

    private static void add(JWTCreator.Builder builder, String name, Object value) {
        switch (value) {
            case String text -> builder.withClaim(name, text);
            case Long number -> builder.withClaim(name, number);
            default -> throw new IllegalArgumentException(name);
        }
    }

    public static String signed(Map<String, Object> claims) {
        return signed(claims, Algorithm.HMAC256(SECRET));
    }

    public static String unsigned(Map<String, Object> claims) {
        return unsignedHeader() + "." + signed(claims).split("\\.")[1] + ".";
    }

    public static String withATamperedSignature(String token) {
        String[] parts = token.split("\\.");
        String signature = parts[2];
        String kept = signature.substring(0, signature.length() - TAMPERED_SIGNATURE_SUFFIX.length());
        return parts[0] + "." + parts[1] + "." + kept + TAMPERED_SIGNATURE_SUFFIX;
    }

    private static String unsignedHeader() {
        return Base64.getUrlEncoder().withoutPadding()
                .encodeToString(UNSIGNED_HEADER.getBytes(StandardCharsets.UTF_8));
    }
}
