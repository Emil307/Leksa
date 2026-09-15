package com.uwords.application.testing.statements;

import static com.uwords.application.testing.statements.AccessTokenData.FAR_FUTURE_EXPIRY;
import static com.uwords.application.testing.statements.AccessTokenData.OTHER_SECRET;
import static com.uwords.application.testing.statements.AccessTokenData.OTHER_TOKEN_ID;
import static com.uwords.application.testing.statements.AccessTokenData.SECRET;
import static com.uwords.application.testing.statements.AccessTokenData.SESSION_ID;
import static com.uwords.application.testing.statements.AccessTokenData.TOKEN_ID;
import static com.uwords.application.testing.statements.AccessTokenData.USER_ID;
import static com.uwords.application.testing.statements.AccessTokenData.claimsOf;
import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.catchThrowable;

import com.auth0.jwt.JWT;
import com.auth0.jwt.algorithms.Algorithm;
import com.auth0.jwt.exceptions.SignatureVerificationException;
import com.uwords.application.config.AuthTokenProperties;
import com.uwords.application.security.JwtAccessTokenDecoder;
import com.uwords.application.security.JwtAccessTokenIssuer;
import com.uwords.application.security.SecureRandomRefreshTokenGenerator;
import com.uwords.domain.auth.session.AccessTokenClaims;
import com.uwords.domain.auth.session.VerifiedAccessToken;
import java.time.Instant;
import java.util.List;
import java.util.regex.Pattern;

public class SecurityTokenStatements {

    private static final long ACCESS_TOKEN_TTL_SECONDS = 900;
    private static final long REFRESH_TOKEN_TTL_SECONDS = 2592000;
    private static final int OPAQUE_TOKEN_LENGTH = 43;
    private static final Pattern OPAQUE_TOKEN_PATTERN =
            Pattern.compile("[A-Za-z0-9_-]{" + OPAQUE_TOKEN_LENGTH + "}");
    private static final int EXPECTED_REFRESH_TOKEN_COUNT = 2;
    private static final Instant EXPIRES_AT = Instant.ofEpochSecond(FAR_FUTURE_EXPIRY);

    private final AuthTokenProperties properties = new AuthTokenProperties(
            SECRET, ACCESS_TOKEN_TTL_SECONDS, REFRESH_TOKEN_TTL_SECONDS);
    private final JwtAccessTokenIssuer issuer = new JwtAccessTokenIssuer(properties);
    private final JwtAccessTokenDecoder decoder = new JwtAccessTokenDecoder(properties);
    private final SecureRandomRefreshTokenGenerator generator =
            new SecureRandomRefreshTokenGenerator();

    private AccessTokenClaims claims;
    private AccessTokenClaims otherClaims;
    private String token;
    private String otherToken;
    private VerifiedAccessToken verified;
    private List<String> refreshTokens = List.of();
    private Throwable failure;

    public void givenClaimsForAUserSession() {
        claims = new AccessTokenClaims(USER_ID, SESSION_ID, TOKEN_ID, EXPIRES_AT);
    }

    public void givenTwoClaimSetsDifferingOnlyByTokenId() {
        givenClaimsForAUserSession();
        otherClaims = new AccessTokenClaims(USER_ID, SESSION_ID, OTHER_TOKEN_ID, EXPIRES_AT);
    }

    public void whenTheAccessTokenIsIssued() {
        token = issuer.issue(claims);
    }

    public void whenBothAccessTokensAreIssued() {
        token = issuer.issue(claims);
        otherToken = issuer.issue(otherClaims);
    }

    public void whenTheIssuedTokenIsPresentedToTheGuard() {
        verified = VerifiedAccessToken.of(decoder.decode(token));
    }

    public void whenTheTokenIsVerifiedWithAnotherSecret() {
        failure = catchThrowable(
                () -> JWT.require(Algorithm.HMAC256(OTHER_SECRET)).build().verify(token));
    }

    public void whenTwoRefreshTokensAreGenerated() {
        refreshTokens = List.of(generator.generate(), generator.generate());
    }

    public void assertTheTokenCarriesTheSubjectSessionAndExpiry() {
        assertThat(decoder.decode(token))
                .extractingByKeys("sub", "sid", "exp")
                .containsExactly(USER_ID.toString(), SESSION_ID.toString(), FAR_FUTURE_EXPIRY);
    }

    public void assertTheTokenCarriesTheTokenIdAndTheApiAudience() {
        assertThat(decoder.decode(token)).isEqualTo(claimsOf());
    }

    public void assertTheAccessTokensDiffer() {
        assertThat(token).isNotEqualTo(otherToken);
        assertThat(decoder.decode(token)).isEqualTo(claimsOf(TOKEN_ID));
        assertThat(decoder.decode(otherToken)).isEqualTo(claimsOf(OTHER_TOKEN_ID));
    }

    public void assertTheGuardReadsTheIssuedClaims() {
        assertThat(verified)
                .isEqualTo(new VerifiedAccessToken(USER_ID, SESSION_ID, TOKEN_ID, EXPIRES_AT));
    }

    public void assertTheVerificationIsRefusedAsABadSignature() {
        assertThat(failure).isInstanceOf(SignatureVerificationException.class);
    }

    public void assertTheRefreshTokensAreOpaque() {
        assertThat(refreshTokens).hasSize(EXPECTED_REFRESH_TOKEN_COUNT);
        refreshTokens.forEach(token -> assertThat(OPAQUE_TOKEN_PATTERN.matcher(token).matches())
                .as(token)
                .isTrue());
    }

    public void assertTheRefreshTokensDiffer() {
        assertThat(refreshTokens.get(0)).isNotEqualTo(refreshTokens.get(1));
    }
}
