package com.uwords.application.security;

import com.auth0.jwt.JWT;
import com.auth0.jwt.algorithms.Algorithm;
import com.uwords.application.config.AuthTokenProperties;
import com.uwords.domain.auth.session.AccessTokenClaims;
import com.uwords.domain.auth.session.VerifiedAccessToken;
import com.uwords.usecase.port.auth.session.AccessTokenIssuerPort;
import org.springframework.stereotype.Component;

@Component
public class JwtAccessTokenIssuer implements AccessTokenIssuerPort {

    private final Algorithm algorithm;

    public JwtAccessTokenIssuer(AuthTokenProperties properties) {
        this.algorithm = Algorithm.HMAC256(properties.jwtSecret());
    }

    @Override
    public String issue(AccessTokenClaims claims) {
        return JWT.create()
                .withClaim(VerifiedAccessToken.SUBJECT_CLAIM, claims.subject().toString())
                .withClaim(VerifiedAccessToken.SESSION_CLAIM, claims.sessionId().toString())
                .withJWTId(claims.tokenId().toString())
                .withExpiresAt(claims.expiresAt())
                .withAudience(VerifiedAccessToken.API_AUDIENCE)
                .sign(algorithm);
    }
}
