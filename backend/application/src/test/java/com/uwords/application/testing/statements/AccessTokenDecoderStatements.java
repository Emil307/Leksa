package com.uwords.application.testing.statements;

import static com.uwords.application.testing.statements.AccessTokenData.LONG_PAST_EXPIRY;
import static com.uwords.application.testing.statements.AccessTokenData.MALFORMED_TOKEN;
import static com.uwords.application.testing.statements.AccessTokenData.OTHER_AUDIENCE;
import static com.uwords.application.testing.statements.AccessTokenData.OTHER_SECRET;
import static com.uwords.application.testing.statements.AccessTokenData.SECRET;
import static com.uwords.application.testing.statements.AccessTokenData.UNKNOWN_CLAIM;
import static com.uwords.application.testing.statements.AccessTokenData.UNKNOWN_CLAIM_VALUE;
import static com.uwords.application.testing.statements.AccessTokenData.claimsOf;
import static com.uwords.application.testing.statements.AccessTokenData.signed;
import static com.uwords.application.testing.statements.AccessTokenData.unsigned;
import static com.uwords.application.testing.statements.AccessTokenData.withATamperedSignature;
import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.catchThrowable;

import com.auth0.jwt.algorithms.Algorithm;
import com.uwords.application.config.AuthTokenProperties;
import com.uwords.application.security.JwtAccessTokenDecoder;
import com.uwords.domain.auth.failure.AuthFailureReason;
import com.uwords.domain.auth.failure.Unauthorized;
import com.uwords.domain.common.UnauthorizedException;
import java.util.HashMap;
import java.util.Map;

public class AccessTokenDecoderStatements {

    private static final String OTHER_ALGORITHM_SECRET = SECRET;
    private static final String REASON_FIELD = "reason";
    private static final long ANY_TTL = 900;

    private final JwtAccessTokenDecoder decoder =
            new JwtAccessTokenDecoder(new AuthTokenProperties(SECRET, ANY_TTL, ANY_TTL));

    private Map<String, Object> signedClaims = Map.of();
    private String token = MALFORMED_TOKEN;
    private Map<String, Object> decoded = Map.of();
    private UnauthorizedException failure;

    private void present(Map<String, Object> claims, String presentedToken) {
        signedClaims = claims;
        token = presentedToken;
    }

    public void givenCorrectlySignedTokenCarryingAnUnknownClaim() {
        Map<String, Object> claims = new HashMap<>(claimsOf());
        claims.put(UNKNOWN_CLAIM, UNKNOWN_CLAIM_VALUE);
        present(claims, signed(claims));
    }

    public void givenCorrectlySignedTokenWhoseExpiryHasPassed() {
        Map<String, Object> claims = claimsOf(LONG_PAST_EXPIRY, AccessTokenData.API_AUDIENCE);
        present(claims, signed(claims));
    }

    public void givenCorrectlySignedTokenAddressedToAnotherAudience() {
        Map<String, Object> claims = claimsOf(AccessTokenData.FAR_FUTURE_EXPIRY, OTHER_AUDIENCE);
        present(claims, signed(claims));
    }

    public void givenTokenSignedWithAnotherSecret() {
        Map<String, Object> claims = claimsOf();
        present(claims, signed(claims, Algorithm.HMAC256(OTHER_SECRET)));
    }

    public void givenTokenWhoseSignatureWasTamperedWith() {
        Map<String, Object> claims = claimsOf();
        present(claims, withATamperedSignature(signed(claims)));
    }

    public void givenTokenDeclaringAnotherAlgorithm() {
        Map<String, Object> claims = claimsOf();
        present(claims, signed(claims, Algorithm.HMAC512(OTHER_ALGORITHM_SECRET)));
    }

    public void givenUnsignedToken() {
        Map<String, Object> claims = claimsOf();
        present(claims, unsigned(claims));
    }

    public void givenStructurallyMalformedToken() {
        present(Map.of(), MALFORMED_TOKEN);
    }

    public void whenTheTokenIsDecoded() {
        decoded = decoder.decode(token);
    }

    public void whenDecodingIsAttempted() {
        failure = (UnauthorizedException) catchThrowable(() -> decoder.decode(token));
    }

    public void assertDecodedClaimsAreTheSignedOnes() {
        assertThat(decoded).hasSameSizeAs(signedClaims);
        signedClaims.forEach((name, value) -> assertThat(numeric(decoded.get(name)))
                .as(name)
                .isEqualTo(numeric(value)));
    }

    public void assertDecodingRefusedAsSignature() {
        assertThat(failure).isNotNull();
        assertThat(failure.getMessage()).isEqualTo(Unauthorized.UNAUTHORIZED_MESSAGE);
        assertThat(failure.payload())
                .isEqualTo(Map.of(REASON_FIELD, AuthFailureReason.SIGNATURE.value()));
        assertThat(failure.exposeToUser()).isFalse();
    }

    private static Object numeric(Object value) {
        return value instanceof Number number ? number.longValue() : value;
    }
}
