package com.uwords.application.config;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Positive;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.validation.annotation.Validated;

@Validated
@ConfigurationProperties(prefix = "auth.token")
public record AuthTokenProperties(
        @NotBlank String jwtSecret,
        @Positive long accessTokenTtlSeconds,
        @Positive long refreshTokenTtlSeconds) {
}
