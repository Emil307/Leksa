package com.uwords.application.security;

import com.auth0.jwt.JWT;
import com.auth0.jwt.algorithms.Algorithm;
import com.auth0.jwt.interfaces.DecodedJWT;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.uwords.application.config.AuthTokenProperties;
import com.uwords.domain.auth.failure.AuthFailureReason;
import com.uwords.domain.auth.failure.Unauthorized;
import com.uwords.usecase.port.auth.session.AccessTokenDecoderPort;
import java.io.IOException;
import java.util.Base64;
import java.util.Map;
import org.springframework.stereotype.Component;

@Component
public class JwtAccessTokenDecoder implements AccessTokenDecoderPort {

    private static final TypeReference<Map<String, Object>> CLAIMS = new TypeReference<>() {
    };

    private final Algorithm algorithm;
    private final ObjectMapper payloads;

    public JwtAccessTokenDecoder(AuthTokenProperties properties) {
        this.algorithm = Algorithm.HMAC256(properties.jwtSecret());
        this.payloads = new ObjectMapper();
    }

    @Override
    public Map<String, Object> decode(String token) {
        try {
            DecodedJWT decoded = JWT.decode(token);
            if (!algorithm.getName().equals(decoded.getAlgorithm())) {
                throw Unauthorized.of(AuthFailureReason.SIGNATURE);
            }
            algorithm.verify(decoded);
            return payloads.readValue(Base64.getUrlDecoder().decode(decoded.getPayload()), CLAIMS);
        } catch (RuntimeException | IOException refusal) {
            throw Unauthorized.of(AuthFailureReason.SIGNATURE);
        }
    }
}
